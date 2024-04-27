from datetime import datetime, timedelta
from typing import Any, List

from passlib.context import CryptContext
from alibabacloud_sts20150401.client import Client as Sts20150401Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_sts20150401 import models as sts_20150401_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from core.config import settings
from utils import log

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


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