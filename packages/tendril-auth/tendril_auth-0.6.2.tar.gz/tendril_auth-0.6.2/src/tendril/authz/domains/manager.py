

import importlib

from tendril.jwt.common import register_domain
from tendril.utils.versions import get_namespace_package_names
from tendril.utils import log
logger = log.get_logger(__name__)


class AuthzDomainsManager(object):
    def __init__(self, prefix):
        self._prefix = prefix
        self._domains = {}
        self._find_domains()
        self.finalized = False

    def _find_domains(self):
        logger.info("Searching for authz domains in {0}".format(self._prefix))
        modules = list(get_namespace_package_names(self._prefix))
        for m_name in modules:
            if m_name == __name__:
                continue
            m = importlib.import_module(m_name)
            logger.info("Loading authz domains from {0}".format(m_name))
            self._domains.update(m.domains)
            for domain, obj in m.domains.items():
                if obj.jwt_spec:
                    register_domain(domain, obj.jwt_spec)

    def finalize(self):
        self.finalized = True

    async def upsert(self, user, first_login):
        for domain in self._domains.values():
            await domain.upsert(user, first_login)

    @property
    def domain(self):
        return self._domains
