

from httpx import Auth
from tendril.authn import provider
from tendril import config

from tendril.utils import log
logger = log.get_logger(__name__, log.DEBUG)


class IntramuralAuthenticator(Auth):
    requires_response_body = True

    def __init__(self, service):
        self._realm = None
        self._audience = None
        self._client_id = None
        self._client_secret = None
        self._get_service_auth_params(service)
        self._access_token = None

    def _get_service_auth_params(self, service):
        params = getattr(config, 'SERVICE_{}_AUTH_PARAMETERS'.format(service.upper()), None)
        if not params:
            raise ValueError("Service {} does not have authentication "
                             "parameters configured".format(service.upper()))
        if params['provider'] != provider.provider_name:
            raise ValueError("Service Authentication Provider must be the same as the application "
                             "authentication provider ")
        self._realm = params['realm']
        self._audience = params['audience']
        self._client_id = params['client_id']
        self._client_secret = params['client_secret']
        self._ssl_verify = params['ssl_verify']

    def sync_auth_flow(self, request):
        raise NotImplementedError

    async def async_auth_flow(self, request):
        if self._access_token:
            request.headers["Authorization"] = "Bearer " + self._access_token
            response = yield request

        if not self._access_token or response.status_code == 401:
            # If the server issues a 401 response, then issue a request to
            # refresh tokens, and resend the request.
            await self.async_get_access_token()
            request.headers["Authorization"] = "Bearer " + self._access_token
            yield request

    async def async_get_access_token(self):
        logger.info(f"Requesting intramural access token for {self._audience} from {provider.provider_name}")
        self._access_token = await provider.get_service_access_token(
            realm=self._realm,
            audience=self._audience,
            client_id=self._client_id,
            client_secret=self._client_secret
        )
        logger.info(f"Got intramural access token for {self._audience}")

