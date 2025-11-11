"""
Tests for Tendril AuthN Pydantic models (Pydantic v2).
Also serves as documentation for correct usage of the upgraded models.

Covers:
 - UserStubTModel
 - M2MClientStubTModel
 - Dynamic mixin via UserStubTMixin()
 - TendrilTBaseModel / TendrilTORMModel features
"""

import pytest
from pydantic import ValidationError, BaseModel

from tendril.authn.pydantic import (
    UserStubTModel,
    M2MClientStubTModel,
    UserStubTMixin,
)
from tendril.utils.pydantic import TendrilTBaseModel, TendrilTORMModel


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture
def user_stub_data():
    return {
        "name": "Alice Example",
        "nickname": "alice",
        "picture": "https://s.gravatar.com/avatar/alice.png",
        "user_id": "auth0|abcd1234",
    }


@pytest.fixture
def m2m_stub_data():
    return {
        "name": "sensor_A1",
        "description": "Temperature Sensor Node",
    }


# ---------------------------------------------------------------------
# Base models
# ---------------------------------------------------------------------
def test_tendril_base_model_config():
    """Verify that Tendril base models expose correct model_config settings."""
    assert TendrilTBaseModel.model_config["validate_by_name"]
    assert TendrilTBaseModel.model_config["arbitrary_types_allowed"]
    assert TendrilTORMModel.model_config["from_attributes"]


def test_tendril_orm_model_from_attributes_behavior():
    """Ensure ORM-compatible model supports from_attributes=True."""
    class DummyORM:
        def __init__(self):
            self.name = "Object"
            self.nickname = "orm_nick"
            self.picture = "https://example.com/pic"
            self.user_id = "auth0|999"

    obj = DummyORM()
    user = UserStubTModel.model_validate(obj,  from_attributes=True)
    assert user.name == "Object"
    assert user.nickname == "orm_nick"
    assert user.user_id == "auth0|999"


# ---------------------------------------------------------------------
# UserStubTModel
# ---------------------------------------------------------------------
def test_user_stub_valid(user_stub_data):
    """A valid UserStubTModel should instantiate without error."""
    user = UserStubTModel(**user_stub_data)
    assert user.name == "Alice Example"
    assert user.nickname == "alice"
    assert user.user_id.startswith("auth0|")
    assert "gravatar" in str(user.picture)


def test_user_stub_invalid_url(user_stub_data):
    """Invalid picture URL should raise ValidationError."""
    user_stub_data["picture"] = "not-a-url"
    with pytest.raises(ValidationError):
        UserStubTModel(**user_stub_data)


def test_user_stub_schema_examples():
    """Ensure examples are correctly embedded in JSON schema."""
    schema = UserStubTModel.model_json_schema()
    expected_examples = {
        "name": "User Full Name",
        "nickname": "nickname",
        "picture": "https://s.gravatar.com/avatar/...",
        "user_id": "auth0|...",
    }

    for field, example in expected_examples.items():
        field_schema = schema["properties"][field]
        # v2: examples are directly under the field schema
        examples = field_schema.get("example")
        assert examples, f"No examples found for field {field}"
        assert example in examples, f"Expected example {example} not found for field {field}"


# ---------------------------------------------------------------------
# M2MClientStubTModel
# ---------------------------------------------------------------------
def test_m2m_stub_valid(m2m_stub_data):
    """A valid M2MClientStubTModel should instantiate correctly."""
    client = M2MClientStubTModel(**m2m_stub_data)
    assert client.name == "sensor_A1"
    assert "Sensor" in client.description


def test_m2m_stub_missing_fields():
    """Missing required fields should raise validation error."""
    with pytest.raises(ValidationError):
        M2MClientStubTModel()


# ---------------------------------------------------------------------
# Dynamic UserStubTMixin
# ---------------------------------------------------------------------
def test_user_stub_mixin_expansion(monkeypatch):
    """Ensure expansion produces a proper UserStubTModel."""
    called = {}

    def fake_expand_user_stub(value, **kwargs):
        called["value"] = value
        # simulate what your real expander returns
        return {
            "name": "Alice Example",
            "nickname": "alice",
            "picture": "https://example.com/pic",
            "user_id": value,
        }

    monkeypatch.setattr("tendril.authn.pydantic._expand_user_stub", fake_expand_user_stub)

    Dynamic = UserStubTMixin(inp="puid", out="user")
    model = Dynamic(puid="auth0|abcd1234")

    assert called["value"] == "auth0|abcd1234"
    assert model.puid == "auth0|abcd1234"
    assert isinstance(model.user, UserStubTModel)
    assert model.user.user_id == "auth0|abcd1234"


def test_user_stub_mixin_field_alias(monkeypatch):
    """
    Demonstrates the model alias structure and serialization behavior.
    """

    def fake_expand_user_stub(value, **kwargs):
        return {
            "name": "Alice Example",
            "nickname": "alice",
            "picture": "https://s.gravatar.com/avatar/alice.png",
            "user_id": value,
        }

    monkeypatch.setattr(
        "tendril.authn.pydantic._expand_user_stub",
        fake_expand_user_stub,
    )

    Dynamic = UserStubTMixin(inp="puid", out="user")

    # Instantiate normally
    model = Dynamic(puid="auth0|abcd1234")

    # Verify fields and output
    assert model.puid == "auth0|abcd1234"
    assert model.user.nickname == "alice"

    dumped = model.model_dump(by_alias=True)
    assert "user" in dumped
    assert dumped["user"]["name"] == "Alice Example"
    assert dumped["user"]["user_id"] == "auth0|abcd1234"


def test_user_stub_mixin_repr_and_dump(monkeypatch):
    """
    Sanity check: ensure model JSON roundtrip and type stability.
    """

    def fake_expand_user_stub(value, **kwargs):
        return {
            "name": "Alice Example",
            "nickname": "alice",
            "picture": "https://s.gravatar.com/avatar/alice.png",
            "user_id": value,
        }

    monkeypatch.setattr(
        "tendril.authn.pydantic._expand_user_stub",
        fake_expand_user_stub,
    )

    Dynamic = UserStubTMixin(inp="puid", out="user")

    model = Dynamic(puid="auth0|wxyz")
    dump = model.model_dump()

    # Structural expectations
    assert "puid" in dump
    assert "user" in dump
    assert dump["user"]["user_id"] == "auth0|wxyz"

    # Ensure re-validation works from dumped JSON
    reloaded = Dynamic.model_validate(dump)
    assert reloaded.user.user_id == "auth0|wxyz"

# ---------------------------------------------------------------------
# Documentation examples
# ---------------------------------------------------------------------
def test_documentation_example_basic_usage(user_stub_data):
    """Demonstrate how downstream code should instantiate and serialize."""
    user = UserStubTModel(**user_stub_data)
    json_data = user.model_dump()
    assert json_data["name"] == "Alice Example"
    assert "picture" in json_data
    # Show serialization as JSON
    json_str = user.model_dump_json()
    assert '"auth0|abcd1234"' in json_str


def test_documentation_example_dynamic_mixin(monkeypatch):
    """Example: creating and using a dynamic mixin model."""

    def fake_expand_user_stub(value, **kwargs):
        return {
            "name": "Alice Example",
            "nickname": "alice",
            "picture": "https://s.gravatar.com/avatar/alice.png",
            "user_id": value,
        }

    monkeypatch.setattr(
        "tendril.authn.pydantic._expand_user_stub",
        fake_expand_user_stub,
    )

    Dynamic = UserStubTMixin(inp="user_ref", out="user")
    obj = Dynamic(user_ref="auth0|xyz")

    # Assert proper structure
    assert obj.user.nickname == "alice"
    # JSON serialization includes alias
    dumped = obj.model_dump(by_alias=True)
    assert "user" in dumped
    assert dumped["user"]["user_id"] == "auth0|xyz"
