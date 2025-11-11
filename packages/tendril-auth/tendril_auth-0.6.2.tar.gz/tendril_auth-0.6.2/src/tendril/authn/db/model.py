

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


class Provider(DeclBase, BaseMixin):
    name = Column(String(50), unique=True)
    users = relationship("User", back_populates="provider")


class UserRoles(DeclBase, BaseMixin, TimestampMixin):
    user_id = Column(Integer(),
                     ForeignKey('User.id', ondelete='CASCADE'),
                     index=True)
    role_id = Column(Integer(),
                     ForeignKey('Role.id', ondelete='CASCADE'),
                     index=True)


class User(DeclBase, BaseMixin, TimestampMixin):
    puid = Column(String(255), nullable=False)

    roles = relationship('Role', secondary=UserRoles.__table__,
                         back_populates='users')

    provider_id = Column(Integer(),
                         ForeignKey('Provider.id'), nullable=False)
    provider = relationship("Provider", back_populates="users")

    __table_args__ = (
        UniqueConstraint('puid', 'provider_id'),
    )


class Role(DeclBase, BaseMixin):
    name = Column(String(50), unique=True)
    description = Column(String(255))
    users = relationship('User', secondary=UserRoles.__table__,
                         back_populates='roles')
