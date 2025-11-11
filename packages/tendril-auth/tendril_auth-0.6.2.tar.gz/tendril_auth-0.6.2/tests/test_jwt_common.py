import pytest
import datetime

import tendril.jwt.common as common


class DummyDomain:
    """Minimal stand-in for AuthzDomainBase."""
    def __init__(self, name):
        self.name = name


@pytest.fixture(autouse=True)
def reset_domains():
    """Reset the global domain registry before and after each test."""
    common.domains.clear()
    yield
    common.domains.clear()


def make_mock_logger(capture):
    """Create a lightweight mock logger that captures info/warn calls."""
    class MockLogger:
        def info(self, msg, *args, **kwargs):
            try:
                capture["info"] = msg % args if args else msg
            except Exception:
                capture["info"] = msg
        def warning(self, msg, *args, **kwargs):
            try:
                capture["warn"] = msg % args if args else msg
            except Exception:
                capture["warn"] = msg
    return MockLogger()


def test_register_domain_adds_entry(monkeypatch):
    """Registers a new domain and ensures it appears in the registry."""
    dummy = DummyDomain("grafana")
    called = {}
    mock_logger = make_mock_logger(called)

    monkeypatch.setattr(common, "logger", mock_logger)

    common.register_domain("grafana", dummy)

    assert "grafana" in common.domains
    assert common.domains["grafana"] is dummy
    assert "Registered Authz JWT domain" in called["info"]


def test_register_domain_overwrites(monkeypatch):
    """If a domain is re-registered, it should overwrite and log a warning."""
    dummy1 = DummyDomain("one")
    dummy2 = DummyDomain("two")
    called = {}
    mock_logger = make_mock_logger(called)

    monkeypatch.setattr(common, "logger", mock_logger)

    common.register_domain("grafana", dummy1)
    common.register_domain("grafana", dummy2)

    assert common.domains["grafana"] is dummy2
    assert "already registered" in called["warn"]
    assert "Registered Authz JWT domain" in called["info"]


def test__now_utc_returns_aware_datetime():
    """_now_utc should return a timezone-aware datetime in UTC."""
    now = common._now_utc()
    assert isinstance(now, datetime.datetime)
    assert now.tzinfo is not None
    assert now.tzinfo.utcoffset(now) == datetime.timedelta(0)
    # The time should be within a reasonable range of "now"
    delta = datetime.datetime.now(datetime.timezone.utc) - now
    assert abs(delta.total_seconds()) < 2
