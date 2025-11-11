

import urllib
import validators
from typing import Dict, Any

from tendril.config import AUTH_AUDIENCE_BASE
from tendril.utils.log import get_logger
logger = get_logger(__name__)


class AuthzDomainBase:
    """
    Base class for Tendril authorization domains, geared largely toward
    rich JWT generation.

    Each domain defines, for example:
      - jwt_spec: {
            "claims": {
                "aud": <see get_audience>,
                "sub": "user_email",
            },
            "audience": <see get_audience>,
            "validity": 3600,
            "nbf_offset": 5
        }

    The default JWT structure is *minimal*, matching third-party auth
    handoffs:

        {
            "iss": AUTH_JWT_ISSUER,
            "aud": <domain.audience>,
            "exp": <now + validity + ttl>,
            "nbf": <now + ttl>,
            "iat": <now>,
            "jti": <random uuid>
        }

    All additional claims are populated through jwt_spec['claims'], and
    typically must minimally include:

        {
            "sub": Subject
        }

    """

    jwt_spec: Dict[str, Any] = None

    # ------------------------------------------------------------------
    # Convenience authentication accessors
    # ------------------------------------------------------------------
    def get_user_profile(self, user):
        from tendril.authn.users import get_user_profile
        return get_user_profile(user)

    def get_user_email(self, user):
        from tendril.authn.users import get_user_email
        return get_user_email(user)

    def get_audience(self):
        if self.jwt_spec.get('aud', None) is None:
            return None
        if validators.url(self.jwt_spec['aud']):
            return self.jwt_spec['aud']
        else:
            return urllib.parse.join(AUTH_AUDIENCE_BASE, self.jwt_spec['aud'])

    async def upsert(self, user, first_login):
        raise NotImplementedError


domains = {}
