

from typing import Optional
from functools import lru_cache

"""
This module implements a caching layer around provider-specific `security` functions.

Factory Pattern:
----------------
Each provider defines its own `security(scopes=None)` returning (usually) a FastAPI
Security() dependency. The common layer wraps that function with caching, so that
identical scope combinations reuse the same Security() instance across endpoints and
modules.
"""

def wrap_security(provider_name: str, provider_security):
    """
    Wrap provider_security(scopes=None) with a cache that preserves
    FastAPI's function signature for OpenAPI introspection.
    """
    @lru_cache(maxsize=None)
    def _cached(scopes_key: str):
        scopes = scopes_key.split(" ") if scopes_key else []
        return provider_security(scopes=scopes)

    def security(scopes: Optional[list[str]] = None):
        scope_key = " ".join(sorted(scopes or []))
        return _cached(scope_key)

    return security


def null_dependency():
    return None
