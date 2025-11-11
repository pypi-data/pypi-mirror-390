

from fastapi import APIRouter
from fastapi import Depends
from fastapi import BackgroundTasks

from tendril.apiserver.security import security
from tendril.apiserver.security import swagger_auth
from tendril.apiserver.security import AuthUserModel

from tendril.authn.users import verify_user_registration
from tendril.authn.users import get_user_profile
from tendril.authn.users import get_user_stub


user_services = APIRouter(prefix='/user',
                          tags=["User Authentication Services"],
                          dependencies=[Depends(swagger_auth)])


@user_services.get("/verify")
async def verify(background_tasks: BackgroundTasks,
                 user: AuthUserModel = security()):
    verify_user_registration(user, background_tasks=background_tasks)
    return {"message": "Logged in User Verified."}


@user_services.get("/profile/me")
async def my_profile(user: AuthUserModel = security()):
    return await get_user_profile(user)


@user_services.get("/stub", dependencies=[security()])
async def user_stub(user_id: str):
    return await get_user_stub(user_id)


routers = [
    user_services
]
