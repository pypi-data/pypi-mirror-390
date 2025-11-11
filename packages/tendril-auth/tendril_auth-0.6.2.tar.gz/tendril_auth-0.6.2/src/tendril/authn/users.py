

import inspect
from tendril.authz import domains
from tendril.authn.provider import AuthProvider
from tendril.authn.provider import provider_name

from .db.model import User
from .db.controller import register_user
from .db.controller import get_user_by_id

from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)

AuthUserModel = AuthProvider.AuthUserModel
get_provider_user_profile = AuthProvider.get_user_profile


def preprocess_user(user):
    if isinstance(user, AuthUserModel):
        user = user.id
    elif isinstance(user, User):
        user = user.id
    elif isinstance(user, int):
        user = get_user_by_id(user).puid
    return user


async def get_user_profile(user):
    user = preprocess_user(user)
    profile = {}

    result = get_provider_user_profile(user)
    if inspect.isawaitable(result):
        result = await result
    profile[provider_name] = result
    return profile


async def expand_user_stub(v, **kwargs):
    if inspect.isawaitable(v):
        v = await v
    if isinstance(v, str):
        return await get_user_stub(v)
    return v


async def get_user_stub(user):
    user = preprocess_user(user)
    result = AuthProvider.get_user_stub(user)
    if inspect.isawaitable(result):
        result = await result
    return result


async def get_user_email(user):
    profile = await get_user_profile(user)
    try:
        return profile[provider_name]['email']
    except KeyError:
        raise AttributeError(f"Could not find an email for user {user}")


def verify_user_registration(user, background_tasks=None):
    user_id = preprocess_user(user)
    user, first_login = register_user(user_id, provider_name)
    if background_tasks:
        background_tasks.add_task(domains.upsert,
                                  user=user,
                                  first_login=first_login)
