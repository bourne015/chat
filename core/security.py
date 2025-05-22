from datetime import datetime, timedelta
from typing import Any, List

import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from alibabacloud_sts20150401.client import Client as Sts20150401Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sts20150401 import models as sts_20150401_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from api.deps import db_client
from core.config import settings
from utils import log


SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 43200 # 30days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except Exception as e:
        raise credentials_exception
    user = db_client.user.get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user


class OSS:
    def __init__(self):
        self.client = self.create_client()

    #@staticmethod
    def create_client(self) -> Sts20150401Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id=settings.oss_access_key,
            access_key_secret=settings.oss_access_key_secret
        )
        # Endpoint 请参考 https://api.aliyun.com/product/Sts
        config.endpoint = settings.oss_endpoint
        return Sts20150401Client(config)

    ### @staticmethod
    def get_credentials(self) -> None:
        assume_role_request = sts_20150401_models.AssumeRoleRequest(
            role_arn=settings.oss_role_arn,
            role_session_name=settings.oss_role_session_name,
            duration_seconds=settings.oss_duration_seconds
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = self.client.assume_role_with_options(assume_role_request, runtime)
            if resp.status_code == 200:
                return resp.body.credentials
        except Exception as error:
            print(f"get oss error:{error.message}")
        return None


    async def get_credentials_async(self) -> None:
        assume_role_request = sts_20150401_models.AssumeRoleRequest(
            role_arn=settings.oss_role_arn,
            role_session_name=settings.oss_role_session_name,
            duration_seconds=settings.oss_duration_seconds
        )
        runtime = util_models.RuntimeOptions()
        try:
            resp = await self.client.assume_role_with_options_async(assume_role_request, runtime)
            if resp.status_code == 200:
                return resp.body.credentials
        except Exception as error:
            log.debug(f"get oss error:{error.message}")
        return None

oss = OSS()
