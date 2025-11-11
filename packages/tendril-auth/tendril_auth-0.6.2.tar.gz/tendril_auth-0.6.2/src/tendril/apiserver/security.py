

from tendril.authn.provider import AuthProvider
from tendril.authn.provider import provider_name
from tendril.authn.scaffold import wrap_security
from tendril.authn.scaffold import null_dependency

from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)

# This motif is based on Auth0's auth_dependency, where auth0's implicit scheme is provided
# for swagger integration. If a provider does not need this, it this can be replaced with a
# dummy function that just returns None.
swagger_auth = getattr(AuthProvider, "swagger_auth", null_dependency)
security = wrap_security(provider_name, AuthProvider.security)
AuthUserModel = AuthProvider.AuthUserModel
