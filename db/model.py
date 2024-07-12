# _*_ coding: utf-8 _*_
import time

from dictns import Namespace
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, Boolean, Text


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
    credit = Column(Float(), comment="credit balance", default=0.0)
    active = Column(Boolean(), comment="whether the user is active", default=True)


class Chat(Base):
    '''
    chat data table
    '''
    __tablename__ = 'Chat'
    id = Column(Integer(), primary_key=True, index=True)
    page_id = Column(Integer(), comment="tab id assigned in user level", default=-1)
    user_id = Column(Integer(), ForeignKey(User.id), nullable=False)
    title = Column(String(50), comment="this chat title")
    contents = Column(JSON(), comment="chat content of this title")
    model = Column(String(50), comment="chat model")
    created_at = Column(Integer(), default=None)
    updated_at = Column(Integer(), default=None)
    assistant_id = Column(String(), default=None)
    thread_id = Column(String(), default=None)
    bot_id = Column(Integer(), default=None)


class Bot(Base):
    '''
    bot data table
    '''
    __tablename__ = 'Bot'
    id = Column(Integer(), primary_key=True, index=True)
    assistant_id = Column(String, comment="assistant id")
    name = Column(String(50), comment="bot name", nullable=False)
    avatar = Column(String, comment="bot avatar")
    description = Column(String, comment="bot detail description")
    prompts = Column(String, comment="bot prompts", nullable=False)
    model = Column(String, comment="the default model to use")
    file_search = Column(Boolean(), comment="enable file search or not", default=False)
    vector_store_ids = Column(JSON(), comment="file search file_ids, dict, key: id, val: name}")
    code_interpreter = Column(Boolean(), comment="enable code interpreter or not", default=False)
    code_interpreter_files = Column(JSON(), comment="dict, key: filename, value: file-id")
    functions = Column(JSON(), comment="dict, key: name, value: function body")
    temperature = Column(Float(), comment="sampling temperature, between 0 and 2", default=1.0)
    author_id = Column(Integer(), comment="author id")
    author_name = Column(String(50), comment="author name")
    likes = Column(Integer(), default=0)
    public = Column(Boolean(), comment="public or not", default=True)
    created_at = Column(Integer(), default=None)
    updated_at = Column(Integer(), default=None)


class Shares(Base):
    '''
    shared informations
    '''
    __tablename__ = 'Shares'
    id = Column(Integer(), primary_key=True, index=True)
    bot_updated = Column(Integer(), comment="latest bots update time")