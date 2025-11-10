from http import HTTPStatus
from typing import Dict, Union

import requests

from ghkit.cache import Cache, cacheout
from ghkit.cache.memory_cache import MemoryCache
from ghkit.log import logger

from ..error import AccessTokenError
from .feishu import FeishuBotType, FeishuMessageType, FeishuReceiveType
from .message import build_message


class FeishuAppBot:
    """飞书应用机器人消息发送"""

    # 飞书获取应用鉴权凭证接口
    # 接口文档: https://open.feishu.cn/document/server-docs/authentication-management/access-token/tenant_access_token_internal
    TENANT_ACCESS_TOKEN_INTERNAL_API = (
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    )

    # 飞书发送消息接口
    # 接口文档: https://open.feishu.cn/document/server-docs/im-v1/message/create
    MESSAGE_CREATE_API = "https://open.feishu.cn/open-apis/im/v1/messages"

    def __init__(self, app_id: str = None, app_secret: str = None, cache: Cache = None) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.cache = cache or MemoryCache()

        self.get_tenant_access_token = cacheout(
            cache=self.cache, ttl=7200, key_name="tenant_access_token"
        )(self.get_tenant_access_token)

    @classmethod
    def expect_token(cls, response: requests.Response) -> str:
        """
        处理HTTP响应，确保成功，并检查业务逻辑的错误。
        :param response:
        :return:
        """
        # 检查HTTP状态码
        if response.status_code != HTTPStatus.OK:
            response.raise_for_status()

        # 解析相应内容
        data = response.json()

        # 检查业务逻辑错误
        if data.get("code") != 0:
            raise ValueError(data.get("msg", "Unknown error"))

        # 检查并返回访问令牌
        token = data.get("tenant_access_token")
        if not token:
            raise ValueError("Token not found in response")
        return token

    def get_tenant_access_token(self):
        """获取应用鉴权凭证"""
        try:
            response = requests.post(
                url=self.TENANT_ACCESS_TOKEN_INTERNAL_API,
                json={
                    "app_id": self.app_id,
                    "app_secret": self.app_secret,
                },
                timeout=30,
            )
            return self.expect_token(response)
        except Exception as e:
            logger.error(f"Get tenant access token error: {str(e)}")
            raise AccessTokenError("An error occurred while get tenant access token") from e

    def send(
        self,
        receive_id: str,
        receive_id_type: FeishuReceiveType,
        message: Union[str, Dict],
        message_type: FeishuMessageType = FeishuMessageType.TEXT,
        timeout: int = 30,
    ) -> None:
        """
        同步发送应用机器人消息
        :param receive_id:
        :param receive_id_type:
        :param message:
        :param message_type:
        :param timeout:
        :return:
        """
        msg = build_message(message, message_type, FeishuBotType.APPLICATION)
        msg.send(
            url=self.MESSAGE_CREATE_API,
            receive_id=receive_id,
            timeout=timeout,
            params={"receive_id_type": receive_id_type.value},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.get_tenant_access_token()}",
            },
        )

    async def async_send(
        self,
        receive_id: str,
        receive_id_type: FeishuReceiveType,
        message: Union[str, Dict],
        message_type: FeishuMessageType = FeishuMessageType.TEXT,
        timeout: int = 30,
    ):
        """
        异步发送应用机器人消息
        :param receive_id:
        :param receive_id_type:
        :param message:
        :param message_type:
        :param timeout:
        :return:
        """
        msg = build_message(message, message_type, FeishuBotType.APPLICATION)
        await msg.async_send(
            url=self.MESSAGE_CREATE_API,
            receive_id=receive_id,
            timeout=timeout,
            params={"receive_id_type": receive_id_type.value},
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.get_tenant_access_token()}",
            },
        )
