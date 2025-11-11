

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declared_attr


class UserMixin(object):
    @declared_attr
    def user_id(cls):
        return Column(Integer(), ForeignKey('User.id'), nullable=False)

    @declared_attr
    def user(cls):
        return relationship("User")
