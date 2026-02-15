from contextlib import asynccontextmanager
from typing import Dict, List

from fastapi import Depends, FastAPI, Request, status
from pydantic import EmailStr

from core.setup import get_db, settings
from routes.auth_routes import router as auth_router
from routes.task_routes import router as task_router
from routes.user_routers import router as user_router
from schemas.user_schemas import UserSchema
from services.auth_validation import get_current_auth_user
from services.user_services import create_user
from utils.rate_limit import (
    get_auth_rate_limit,
    get_global_rate_limit,
    get_user_rate_limit,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    import asyncio

    from core.redis import redis_manager
    from utils.auth_helper import TokenBlackList

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


app = FastAPI(lifespan=lifespan, dependencies=[Depends(get_global_rate_limit)])

app.include_router(user_router, dependencies=[Depends(get_user_rate_limit)])
app.include_router(task_router, dependencies=[Depends(get_user_rate_limit)])
app.include_router(auth_router, dependencies=[Depends(get_auth_rate_limit)])


@app.post(
    "/users/",
    tags=["users"],
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_user_handle(user: UserSchema = Depends(create_user)):
    return user


@app.get("/jwt/forgot-password/", tags=["jwt"])
async def forgot_password(email: EmailStr, session=Depends(get_db)):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    from services.user_services import get_user_by_email
    from utils.auth_helper import create_access_token

    server = smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT)
    server.starttls()
    server.login(settings.MAIL_FROM, settings.APP_PASSWORD_SECRET)

    msg = MIMEMultipart()
    msg["From"] = settings.MAIL_FROM
    msg["To"] = email
    msg["Subject"] = "Token for account reset"

    user = await get_user_by_email(email, session)
    token = create_access_token(user)

    msg.attach(
        MIMEText(
            f"""Here is token for deleting your account: 
            "
            {token}
            "
            thanks for using our service!""",
            "plain",
        )
    )

    server.send_message(msg)

    return {"detail": f"Token has been sent to {email} if it exists in our system."}


@app.get("/", response_model=Dict[str, str], summary="User greeter")
async def root_func(rate_limiter=Depends(get_global_rate_limit)):
    return {"message": "hello world"}


@app.put(
    "/",
    response_model=Dict[str, str],
    summary="Data resetter to default",
    description="resets data to default data (test_data.json)",
)
async def refresh_data(
    session=Depends(get_db), rate_limiter=Depends(get_global_rate_limit)
):
    from utils.data_helper import add_data_into_db, recreate_tables

    await recreate_tables()
    await add_data_into_db(session)
    return {"message": "Tables were recreated!"}


@app.post(
    "/blacklist",
    response_model=List | Dict,
    summary="Token Blacklist only for admin",
    description="If you are admin, shows which tokens have been blacklisted",
)
async def see_the_blacklist(
    request: Request,
    user=Depends(get_current_auth_user),
    rate_limiter=Depends(get_global_rate_limit),
):
    admin_email = "admin@example.com"

    if user.email == admin_email:
        return request.app.state.blacklist.jti_to_expiry_blacklist
    else:
        return {"Message": f"{user.username} you are not admin"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)


# TODO: Database Token Storage
# TODO: add forgot-password and reset-password endpoints with email sending, using kafka
