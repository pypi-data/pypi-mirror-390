import json
import time
from http import HTTPStatus
from typing import Dict, Union

import httpx
import requests

from ghkit.log import logger
from ghkit.messenger import Message
from ghkit.messenger.dingtalk import DingTalkMessageType, gen_sign
from ghkit.messenger.error import MessageTypeError


class DingTalkMessage(Message):

    @classmethod
    def handler_response(cls, response):
        """
        处理HTTP响应，确保成功，并检查业务逻辑的错误。
        :param response:
        :return:
        """

        if response.status_code != HTTPStatus.OK:
            logger.error(f"{response.text}")
            response.raise_for_status()

        data = response.json()
        if data.get("errcode") != 0:
            raise ValueError(data.get("errmsg", "Unknown error"))

    def __init__(self, msg_data: Dict) -> None:
        super().__init__(msg_data)
        self.req_params = dict()
        self.webhook_url = "https://oapi.dingtalk.com/robot/send"

    def handle_secret(self, secret):
        if secret:
            timestamp = round(time.time() * 1000)
            sign = gen_sign(timestamp, secret)
            self.req_params["sign"] = sign
            self.req_params["timestamp"] = timestamp

    def send(self, token: str, secret: str = None, timeout: int = 0, **kwargs) -> None:
        """
        同步发送消息
        :param token:
        :param secret:
        :param timeout:
        :return:
        """
        try:
            self.req_params["access_token"] = token
            self.handle_secret(secret)
            response = requests.post(
                url=self.webhook_url,
                params=self.req_params,
                json=self.msg_data,
                timeout=timeout,
                **kwargs,
            )
            self.handler_response(response)
        except Exception as e:
            self.handle_send_error(e)

    async def async_send(self, token: str, secret: str = None, timeout: int = 0, **kwargs) -> None:
        """
        异步发送消息
        :param token:
        :param secret:
        :param timeout:
        :return:
        """
        try:
            self.req_params["access_token"] = token
            self.handle_secret(secret)
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url=self.webhook_url, json=self.msg_data, timeout=timeout, **kwargs
                )
                self.handler_response(response)
        except Exception as e:
            self.handle_send_error(e)

    def __repr__(self):
        return json.dumps(self.msg_data, ensure_ascii=False)


class TextMessage(DingTalkMessage):
    def __init__(self, text: str) -> None:
        msg_data = {"msgtype": "text", "text": {"content": text}}
        super().__init__(msg_data)


def build_message(
    message: Union[str, Dict],
    message_type: DingTalkMessageType,
) -> DingTalkMessage:
    """
    构建消息
    :param message:
    :param message_type:
    :return:
    """
    # 根据消息类型构建消息对象
    if message_type == DingTalkMessageType.TEXT:
        return TextMessage(message)
    else:
        raise MessageTypeError
