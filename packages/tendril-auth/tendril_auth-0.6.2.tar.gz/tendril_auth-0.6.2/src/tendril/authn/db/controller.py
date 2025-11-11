

from sqlalchemy.orm.exc import NoResultFound
from tendril.utils.db import with_db

from .model import User
from .model import Provider

from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


@with_db
def get_users(session=None):
    pass


@with_db
def get_user(puid, provider=None, session=None):
    filters = [User.puid == puid]
    if provider:
        filters.append(User.provider == provider)
    q = session.query(User).filter(*filters)
    return q.one()


@with_db
def get_user_by_id(id, session=None):
    return session.query(User).get(id)


@with_db
def get_provider(name, session=None):
    q = session.query(Provider).filter_by(name=name)
    return q.one()


@with_db
def register_provider(name, must_create=False, session=None):
    if name is None:
        raise AttributeError("name cannot be None")

    try:
        existing = get_provider(name)
    except NoResultFound:
        provider = Provider(name=name)
    else:
        if must_create:
            raise ValueError("Provider Already Exists")
        else:
            provider = existing
    session.add(provider)
    return provider


@with_db
def register_user(puid, provider, must_create=False, session=None):
    if puid is None:
        raise AttributeError("puid cannot be None")
    if provider is None:
        raise AttributeError("provider cannot be None")

    if not isinstance(provider, Provider):
        provider = get_provider(name=provider, session=session)

    try:
        q = session.query(User).filter_by(
            puid=puid, provider=provider
        )
        existing = q.one()
    except NoResultFound:
        logger.info("Registering user '{}' from provider '{}'"
                    "".format(puid, provider.name))
        first_login = True
        user = User(puid=puid, provider=provider, provider_id=provider.id)
    else:
        if must_create:
            raise ValueError("User Already Exists")
        else:
            logger.info("Using existing user '{}' for {} user '{}'"
                        "".format(existing.id, provider.name, puid))
            user = existing
            first_login = False
    session.add(user)
    first_login = True
    return user, first_login


@with_db
def preprocess_user(user, provider=None, session=None):
    if user is None:
        raise AttributeError("user cannot be None")
    if hasattr(user, 'id'):
        # TODO This is a somewhat special case to strip down Auth0User
        #      instances. A more generic approachmay be useful in the future.
        user = user.id
    if isinstance(user, int):
        user_id = user
    elif isinstance(user, User):
        user_id = user.id
    else:
        try:
            user = get_user(user, provider, session=session)
            user_id = user.id
        except NoResultFound:
            raise AttributeError(f"User {user} does not seem to exist.")
    return user_id
