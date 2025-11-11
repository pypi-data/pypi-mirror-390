

from typing import Any
from typing import Union
from typing import Optional

from pydantic import Field
from pydantic import create_model
from pydantic import model_validator

from tendril.utils.pydantic import TendrilTBaseModel
from tendril.utils.pydantic import StrHttpUrl

UserReferenceTModel = Union[int, str]


class UserStubTModel(TendrilTBaseModel):
    name: str = Field(..., json_schema_extra={'example': "User Full Name"})
    nickname: str = Field(..., json_schema_extra={'example': 'nickname'})
    picture: StrHttpUrl = Field(..., json_schema_extra={'example': 'https://s.gravatar.com/avatar/...'})
    user_id: str = Field(..., json_schema_extra={'example': 'auth0|...'})


class M2MClientStubTModel(TendrilTBaseModel):
    name: str = Field(..., json_schema_extra={"example": "some_name"})
    description: str = Field(..., json_schema_extra={"example": "Some Description"})


def _expand_user_stub(*args, **kwargs):
    """Defer import to avoid circular dependency."""
    from tendril.authn.users import expand_user_stub
    return expand_user_stub(*args, **kwargs)


def UserStubTMixin(inp: str = "puid", out: str = "user"):
    """
    Dynamic mixin that auto-expands a user stub from a puid.

    - <inp> : Raw user reference string (required)
    - <out> : Auto-populated expanded user stub (UserStubTModel or M2MClientStubTModel)
    """

    fields = {
        inp: (str, Field(..., description="Raw user reference ID (puid)")),
        out: (
            Optional[Union[UserStubTModel, M2MClientStubTModel]],
            Field(default=None, description="Expanded user stub (auto-generated)"),
        ),
    }

    def _populate_user_stub(cls, data: Any):
        """
        Automatically populate the expanded user stub.
        Ensures the resulting object is a proper Pydantic model.
        """
        if not isinstance(data, dict):
            return data

        if data.get(out) is None and data.get(inp):
            expanded = _expand_user_stub(data[inp])
            if isinstance(expanded, dict):
                # Default to UserStubTModel unless keys imply M2MClientStubTModel
                if "description" in expanded and "name" in expanded:
                    data[out] = M2MClientStubTModel(**expanded)
                else:
                    data[out] = UserStubTModel(**expanded)
            elif isinstance(expanded, (UserStubTModel, M2MClientStubTModel)):
                data[out] = expanded
            else:
                raise TypeError(
                    f"Invalid expansion result type for {inp}: {type(expanded).__name__}"
                )
        return data

    DynamicModel = create_model(
        f"UserStubTModel_{inp}_{out}",
        **fields,
        __base__=TendrilTBaseModel,
        __validators__={
            "_populate_user_stub": model_validator(mode="before")(_populate_user_stub)
        },
    )

    DynamicModel.model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }

    return DynamicModel
