

from tendril.authz.domains.base import AuthzDomainBase
from tendril.utils import log
logger = log.get_logger(__name__)


class ScopesAuthzDomain(AuthzDomainBase):
    async def upsert(self, user, first_login):
        from tendril.authz.connector import add_user_scopes
        from tendril.authz.scopes import default_user_scopes
        if first_login and default_user_scopes:
            logger.debug(f"Writing user {user.puid} default scopes")
            add_user_scopes(user.puid, default_user_scopes)

        # TODO Consider triggering a more thorough scope updation here.
        #   Note that as it stands right now, it's pretty seriously
        #   complicated, requiring determining assignable scopes from
        #   every interest the user is associated with. Instead, we need
        #   to be able to get the types of interests the user has and
        #   associated role sets. This should be solved alongside the more
        #   streamlined possible_parents:any APIs to be added to check if
        #   create forms should be rendered on the UI.


domains = {
    'scopes': ScopesAuthzDomain()
}
