

from typing import Dict
from datetime import datetime
from datetime import timezone

# Actually importing this causes a circular import.
# from tendril.authz.domains.base import AuthzDomainBase

from tendril.utils.log import get_logger
logger = get_logger(__name__)


# ---------------------------------------------------------------------
# Domain registry
# ---------------------------------------------------------------------
domains: Dict[str, "AuthzDomainBase"] = {}

def register_domain(domain: str, spec: "AuthzDomainBase") -> None:
    """
    Register an AuthzDomainBase instance to the signer.

    Example:
        from tendril.authz.domains.grafana import GrafanaAuthzDomain
        register_domain("grafana", GrafanaAuthzDomain())
    """
    if domain in domains:
        logger.warning("Domain %s is already registered, overwriting.", domain)
    domains[domain] = spec
    logger.info("Registered Authz JWT domain: %s", domain)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)
