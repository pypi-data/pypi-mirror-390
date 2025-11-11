

from tendril.utils.config import ConfigOption
from tendril.utils.config import ConfigOptionConstruct
from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)

depends = ['tendril.config.core',
           'tendril.config.auth']


class ServiceAuthParameters(ConfigOptionConstruct):
    @property
    def value(self):
        return {
            'provider': self.ctx["SERVICE_{}_AUTH_PROVIDER".format(self._parameters)],
            'realm': self.ctx["SERVICE_{}_AUTH_REALM".format(self._parameters)],
            'audience': self.ctx["SERVICE_{}_AUDIENCE".format(self._parameters)],
            'client_id': self.ctx["SERVICE_{}_CLIENT_ID".format(self._parameters)],
            'client_secret': self.ctx["SERVICE_{}_CLIENT_SECRET".format(self._parameters)],
            'ssl_verify': self.ctx["SERVICE_{}_SSL_VERIFICATION".format(self._parameters)],
        }


def _service_auth_config_template(service):
    return [
        ConfigOption(
            'SERVICE_{}_AUTH_PROVIDER'.format(service.upper()),
            "AUTH_PROVIDER",
            "Auth Provider which controls access to the {} service. Note that this is typically the same "
            "as the main auth provider, and use of multiple auth providers in a single instance or "
            "component is not presently tested or supported.".format(service)
        ),
        ConfigOption(
            'SERVICE_{}_AUTH_REALM'.format(service.upper()),
            f"AUTH_REALM",
            "Realm to for the {} service, if different from the Application's Realm".format(service)
        ),
        ConfigOption(
            'SERVICE_{}_AUDIENCE'.format(service.upper()),
            f"None",
            f"Audience to request in service access token for the {service} service."
            f" Expect Deprecation of this unused configuration item."
        ),
        ConfigOption(
            'SERVICE_{}_CLIENT_ID'.format(service.upper()),
            "None",
            f"Client ID to use for authenticating to the {service} service."
        ),
        ConfigOption(
            'SERVICE_{}_CLIENT_SECRET'.format(service.upper()),
            "None",
            f"Client Secret to use for authenticating to the {service} service.",
            masked=True
        ),
        ConfigOption(
            'SERVICE_{}_SSL_VERIFICATION'.format(service.upper()),
            "True",
            f"Whether SSL needs to be verified when authenticating to the {service} service."
        ),
        ServiceAuthParameters(
            'SERVICE_{}_AUTH_PARAMETERS'.format(service.upper()),
            service.upper(),
            f"Constructed Service Auth parameters instance for the "
            f"{service} service. This option is created by the code, and should not "
            f"be set directly in any config file."
        )
    ]


def load(manager):
    logger.debug("Loading {0}".format(__name__))
    config_elements_service_auth = []
    for service in manager.SERVICES:
        config_elements_service_auth += _service_auth_config_template(service)
    manager.load_elements(config_elements_service_auth,
                          doc="Authentication to Available Services")
