

from tendril.config import AUTH_PROVIDER
from tendril.config import AUTH_INTRAMURAL_TOKEN_CACHING
from tendril.utils.fsutils import load_provider

from .db.controller import register_provider

from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)

try:
    AuthProvider = load_provider(AUTH_PROVIDER, "tendril.authn.providers")
    provider_name = AUTH_PROVIDER
except ImportError as e:
    logger.critical(e)
    raise


def _cache_key_func(audience, client_id, client_secret):
    return f"{provider_name}:{client_id}:{audience}"


if AUTH_INTRAMURAL_TOKEN_CACHING == 'platform':
    logger.info("Using platform level caching for Intramural Authentication Tokens")
    from tendril.caching import platform_cache as intramural_cache
else:
    logger.info("Not caching Intramural Authentication Tokens")
    from tendril.caching import no_cache as intramural_cache


@intramural_cache(namespace='intramuraltokens', ttl=3600, key=_cache_key_func)
async def get_service_access_token(realm, audience, client_id, client_secret, ssl_verify=True):
    """
    Generic API for intramural authenticators to request access tokens.
    Each provider module (Auth0, Keycloak, etc.) must implement this.
    """
    if not hasattr(AuthProvider, "get_service_access_token"):
        raise NotImplementedError(
            f"AuthProvider {provider_name} does not implement get_service_access_token"
        )

    return await AuthProvider.get_service_access_token(realm, audience, client_id, client_secret, ssl_verify)

def init():
    AuthProvider.init()
    register_provider(provider_name)

init()
