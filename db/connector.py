#!/usr/bin/env python
# _*_ coding: utf-8 _*_
import concurrent.futures
import logging as log

from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.user import UserDBConnectorComponent
from db.chat import ChatDBConnectorComponent
from db.bot import BotDBConnectorComponent


@contextmanager
def session_scope(Session=None):
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as exce:
        session.rollback()
        raise Exception from exce
    finally:
        session.close()


class DBClient():
    '''
    Used to operate the database.
    We'd prefer high level api to set mysql driver to make our internace common
    Input: dburl : dburl = "mysql+{driver}://{user}:{pwd}@{server}:{port}/{db}?charset=utf8mb4"
    '''
    POOL_SIZE = 10
    TAG = 'DBTreadPool'

    def __init__(self, db_url=None, connect_args=None):
        self.db_url = db_url
        self.engine = None
        self.scoped_session = None
        # pylint: disable = consider-using-with
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.POOL_SIZE,
                                                          thread_name_prefix=self.TAG)

        self._init_session(connect_args)

        self.user = UserDBConnectorComponent(self)
        self.chat = ChatDBConnectorComponent(self)
        self.bot = BotDBConnectorComponent(self)

    def _init_session(self, connect_args):
        if connect_args:
            # SQLite objects created in a thread can only be used in that same thread
            self.engine = create_engine(self.db_url, pool_pre_ping=True, connect_args={'check_same_thread': False})
        else:
            self.engine = create_engine(self.db_url, pool_pre_ping=True)
        self.Session = sessionmaker(bind=self.engine)

    def execute(self, f):
        data = ''
        try:
            with session_scope(self.Session) as session:
                futuer = self.pool.submit(f, session)
                data = futuer.result()
        except Exception as exce:
            log.error('db.pool cmd {} generated an exception: {}'.format(
                f, exce))

        return data

    def close_connect(self):
        self.pool.shutdown()
        self.engine.dispose()
