import asyncio
from contextlib import asynccontextmanager
from typing import Dict, List

import uvicorn
from fastapi import Depends, FastAPI, Request

from core import get_session
from core.redis import redis_manager
from routes.auth_routes import router as auth_router
from routes.task_routes import router as task_router
from routes.user_routers import router as user_router
from schemas.user_schemas import UserSchema
from services.auth_validation import validate_auth_user
from utils.auth_helper import TokenBlackList
from utils.data_helper import add_data_into_db, recreate_tables
from utils.rate_limit import (
    get_auth_rate_limit,
    get_global_rate_limit,
    get_user_rate_limit,
)

admin_email = "admin@example.com"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    blacklist = TokenBlackList()
    app.state.blacklist = blacklist

    cleanup_task = asyncio.create_task(
        blacklist.start_periodic_cleanup(interval_minutes=15)
    )
    app.state.cleanup_task = cleanup_task
    try:
        await redis_manager.connect()
        print("🔧 Starting Redis connection...")
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        raise

    yield
    print("Shutting down...")

    print("🔧 Closing Redis connection...")
    try:
        await redis_manager.disconnect()
        print("✅ Redis disconnected successfully")
    except Exception as e:
        print(f"⚠️ Error during Redis disconnect: {e}")

    cleanup_task.cancel()
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass


app = FastAPI(lifespan=lifespan)

app.include_router(user_router, dependencies=[Depends(get_user_rate_limit)])
app.include_router(task_router, dependencies=[Depends(get_user_rate_limit)])
app.include_router(auth_router, dependencies=[Depends(get_auth_rate_limit)])


@app.get("/", response_model=Dict[str, str])
async def root_func(rate_limiter=Depends(get_global_rate_limit)):
    return {"message": "hello world"}


@app.put("/", response_model=Dict[str, str])
async def refresh_data(
    session=Depends(get_session), rate_limiter=Depends(get_global_rate_limit)
):
    await recreate_tables()
    await add_data_into_db(session)
    return {"message": "Tables were recreated!"}


@app.post("/blacklist", response_model=List | Dict)
async def see_the_blacklist(
    request: Request,
    user: UserSchema = Depends(validate_auth_user),
    rate_limiter=Depends(get_global_rate_limit),
):
    if user.email == admin_email:
        return request.app.state.blacklist.jti_to_expiry_blacklist
    else:
        return {"Message": f"{user.username} you are not admin"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

# TODO: Logout/Token Revocation, Database Token Storage
# TODO: add forgot-password and reset-password endpoints
# TODO: @router.post(
#     "/login",
#     response_model=TokenResponse,
#     summary="User Login",
#     description="Authenticate user and return JWT tokens",
#     responses={
#         200: {"description": "Successful authentication"},
#         401: {"description": "Invalid credentials"},
#         429: {"description": "Too many requests"}
#     }
# )
# document like this
