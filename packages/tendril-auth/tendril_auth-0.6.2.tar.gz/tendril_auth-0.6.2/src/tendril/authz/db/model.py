
"""
First pass for internal scope and audience handling for tendril authz
backend for use in self-contained deployments. Not tested.
Not currently under active development.
"""

from sqlalchemy import Column
from sqlalchemy import String
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship

from tendril.utils.db import DeclBase
from tendril.utils.db import BaseMixin
from tendril.utils.db import TimestampMixin

from tendril.utils import log
logger = log.get_logger(__name__, log.DEFAULT)


class AuthUserScopes(DeclBase, BaseMixin, TimestampMixin):
    user_id = Column(Integer(),
                     ForeignKey('User.id', ondelete='CASCADE'),
                     index=True)
    scope_id = Column(Integer(),
                      ForeignKey('AuthScope.id', ondelete='CASCADE'),
                      index=True)
    __table_args__ = (
        UniqueConstraint('user_id', 'scope_id', name='uq_user_scope'),
    )


class AuthAudience(DeclBase, BaseMixin):
    name = Column(String(50), unique=True)
    description = Column(String(255))
    service_url = Column(String(255))
    token_ttl = Column(Integer())
    scopes = relationship('AuthScope',
                          back_populates='audience',
                          cascade='all, delete-orphan')


class AuthScope(DeclBase, BaseMixin):
    name = Column(String(50))
    description = Column(String(255))

    audience_id = Column(Integer(),
                         ForeignKey('AuthAudience.id', ondelete='CASCADE'))
    audience = relationship('AuthAudience', back_populates='scopes')

    users = relationship('User', secondary=AuthUserScopes.__table__)
    __table_args__ = (
        UniqueConstraint('name', 'audience_id'),
    )


class AuthRoleScopes(DeclBase, BaseMixin):
    role_id = Column(Integer(),
                     ForeignKey('Role.id', ondelete='CASCADE'),
                     index=True)
    scope_id = Column(Integer(),
                      ForeignKey('AuthScope.id', ondelete='CASCADE'),
                      index=True)
