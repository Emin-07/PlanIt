import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List

import uvicorn
from fastapi import Depends, FastAPI, Request

from auth.routes.auth_routes import router as auth_router
from auth.services.validation import validate_auth_user
from auth.utils.helper import TokenBlackList
from core import get_session
from core.data_helper import add_data_into_db, recreate_tables
from task.routes.task_routes import router as task_router
from user.routes.user_routers import router as user_router
from user.schemas.user_schemas import UserSchema

admin_email = "admin@example.com"


@asynccontextmanager
async def lifespan(app: FastAPI):
    blacklist = TokenBlackList()
    app.state.blacklist = blacklist

    cleanup_task = asyncio.create_task(
        blacklist.start_periodic_cleanup(interval_minutes=15)
    )
    app.state.cleanup_task = cleanup_task

    yield

    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(task_router)
app.include_router(auth_router)


@app.get("/", response_model=Dict[str, str])
async def root_func():
    return {"message": "hello world"}


@app.put("/", response_model=Dict[str, str])
async def refresh_data(session=Depends(get_session)):
    await recreate_tables()
    await add_data_into_db(session)
    return {"message": "Tables were recreated!"}


@app.post("/blacklist", response_model=List | Dict)
async def see_the_blacklist(
    request: Request, user: UserSchema = Depends(validate_auth_user)
):
    if user.email == admin_email:
        return request.app.state.blacklist.blacklisted
    else:
        return {"Message": f"{user.username} you are not admin"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
