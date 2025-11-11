

import importlib

from tendril.config import AUTH_PATCH_SCOPES_ON_STARTUP
from tendril.utils.versions import get_namespace_package_names
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


class ScopesManager(object):
    def __init__(self, prefix):
        self._prefix = prefix
        self._scopes = {}
        self._default_scopes = []
        self._find_scopes()
        self.finalized = False

    def _create_scopes(self):
        from tendril.authz import connector
        connector.commit_scopes(self._scopes)

    def _find_scopes(self):
        logger.debug("Loading authn scopes from {0}".format(self._prefix))
        modules = list(get_namespace_package_names(self._prefix))
        for m_name in modules:
            if m_name == __name__:
                continue
            m = importlib.import_module(m_name)
            logger.debug("Loading scopes from {0}".format(m_name))
            self._scopes.update(m.scopes)
            if hasattr(m, 'default_scopes'):
                self._default_scopes.extend(m.default_scopes)

    def finalize(self):
        self.finalized = True
        if AUTH_PATCH_SCOPES_ON_STARTUP:
            # TODO This causes a circular import which needs to be fixed.
            self._create_scopes()

    @property
    def scopes(self):
        return self._scopes

    @property
    def default_user_scopes(self):
        return self._default_scopes
