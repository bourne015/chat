# _*_ coding: utf-8 _*_
import time

from dictns import Namespace
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Float, ForeignKey, JSON, Boolean, Text
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, Dict
import uuid

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
    avatar_bot = Column(String, comment="bot avatar")
    pwd = Column(String(200), comment="password", nullable=False)
    cat_id = Column(String(50), comment="thread is of cat assistant", default=None)
    created_at = Column(Integer(), default=None)
    updated_at = Column(Integer(), default=None)
    credit = Column(Float(), comment="credit balance", default=0.0)
    active = Column(Boolean(), comment="whether the user is active", default=True)
    settings = Column(JSON(), comment="user settings")


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
    artifact = Column(Boolean(), comment="enable artifact", default=False)
    internet = Column(Boolean(), comment="enable internet", default=False)
    temperature = Column(Float(), comment="model temperature", default=None)


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
    instructions = Column(String, comment="bot instructions", nullable=False)
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


class McpServer(Base):
    __tablename__ = 'mcp'
    id = Column(String, primary_key=True, default=uuid.uuid4, index=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    command = Column(String, nullable=False)
    args = Column(String, nullable=False)
    custom_environment = Column(JSON, default=dict)
    owner_id = Column(Integer, nullable=False)
    owner_name = Column(String, nullable=False)
    is_public = Column(Boolean, default=False)
    description = Column(String, nullable=True)
    created_at = Column(Integer, nullable=False)
    updated_at = Column(Integer, nullable=False)



class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer(), primary_key=True, index=True)
    user_id = Column(Integer(), ForeignKey(User.id), nullable=True)
    name = Column(String, comment="product name", nullable=False)
    out_trade_no = Column(String, comment="product trade number", nullable=False)
    type = Column(String, comment="trade type(alipay|wxpay)", nullable=False)
    pid = Column(String, comment="product id",nullable=False)
    money = Column(String, comment="trade money", nullable=False)
    status = Column(Integer(), comment="trade status(1:success, 0:unpaid)",nullable=False)
    param = Column(String, nullable=True)
    created_at = Column(Integer(), nullable=False)
    updated_at = Column(Integer(), nullable=False)


class Shares(Base):
    '''
    shared informations
    '''
    __tablename__ = 'Shares'
    id = Column(Integer(), primary_key=True, index=True)
    bot_updated = Column(Integer(), comment="latest bots update time")
    mcp_updated = Column(Integer(), comment="latest mcp server update time")
