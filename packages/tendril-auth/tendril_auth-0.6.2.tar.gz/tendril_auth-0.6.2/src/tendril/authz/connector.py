

from tendril.utils.fsutils import load_provider
from tendril.config import AUTHZ_PROVIDER
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


try:
    AuthzProvider = load_provider(AUTHZ_PROVIDER, "tendril.authz.providers")
    provider_name = AUTHZ_PROVIDER
except ImportError as e:
    logger.critical(e)
    raise


def get_current_scopes():
    return AuthzProvider.get_current_scopes()


def commit_scopes(scopes):
    return AuthzProvider.commit_scopes(scopes)


def get_user_scopes(user_id):
    return AuthzProvider.get_user_scopes(user_id)


def add_user_scopes(user_id, scopes):
    return AuthzProvider.add_user_scopes(user_id, scopes)


def remove_user_scopes(user_id, scopes):
    return AuthzProvider.remove_user_scopes(user_id, scopes)
