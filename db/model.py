# _*_ coding: utf-8 _*_
import time

from dictns import Namespace
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, SmallInteger, ForeignKey, JSON, Boolean, Text


Base = declarative_base()


def to_dict(self):
    return Namespace({c.name: getattr(self, c.name, None) for c in self.__table__.columns})


Base.to_dict = to_dict


class User(Base):
    '''
    User data table
    '''
    __tablename__ = 'User'
    id = Column(Integer(), primary_key=True, index=True)
    name = Column(String(50), comment="user name")
    email = Column(String(50), comment="user email", nullable=False)
    phone = Column(String(20), comment="phone number")
    avatar = Column(String, comment="user avatar")
    pwd = Column(String(200), comment="password", nullable=False)
    created_at = Column(Integer(), default=None)
    updated_at = Column(Integer(), default=None)
    active = Column(Boolean(), comment="whether the user is active")


class Chat(Base):
    '''
    chat data table
    '''
    __tablename__ = 'Chat'
    id = Column(Integer(), primary_key=True, index=True)
    user_id = Column(Integer(), ForeignKey(User.id), nullable=False)
    title = Column(String(50), comment="this chat title")
    contents = Column(JSON(), comment="chat content of this title")
    model = Column(String(50), comment="chat model")
    created_at = Column(Integer(), default=None)
    updated_at = Column(Integer(), default=None)
