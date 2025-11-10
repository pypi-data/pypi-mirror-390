import json
from http import HTTPStatus
from typing import Dict

from ghkit.log import logger
from ghkit.messenger.error import SendError


class Message:
    def __init__(self, msg_data: Dict) -> None:
        self.msg_data = msg_data

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
        if data.get("code") != 0:
            raise ValueError(data.get("msg", "Unknown error"))

    @classmethod
    def handle_send_error(cls, exception: Exception) -> None:
        """
        通用异常处理
        :param exception:
        :return:
        """
        logger.error(f"Message send error: {str(exception)}")
        raise SendError("An error occurred while sending the message") from exception

    def send(
        self, url: str, receive_id: str = None, secret: str = None, timeout: int = 0, **kwargs
    ) -> None:
        """
        同步发送消息
        :param url:
        :param receive_id:
        :param secret:
        :param timeout:
        :return:
        """
        raise NotImplementedError("Subclasses must implement send()")

    async def async_send(
        self, url: str, receive_id: str = None, secret: str = None, timeout: int = 0, **kwargs
    ) -> None:
        """
        异步发送消息
        :param url:
        :param receive_id:
        :param secret:
        :param timeout:
        :return:
        """
        raise NotImplementedError

    def __repr__(self):
        return json.dumps(self.msg_data, ensure_ascii=False)
