from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from pydantic import ValidationError
from sqlmodel import Session, create_engine, select

from core.config import settings
from db.connector import DBClient
from utils import log

log = log.Logger(__name__, clevel=log.logging.DEBUG)


def get_db() -> DBClient:
    connector = None
    try:
        connector = DBClient(str(settings.SQLALCHEMY_DATABASE_URI))
    except Exception as err:
        log.debug(f"connect db error with :{err}")

    return connector

db_client = get_db()
