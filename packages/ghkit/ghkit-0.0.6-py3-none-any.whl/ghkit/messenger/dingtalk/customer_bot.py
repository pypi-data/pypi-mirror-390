from typing import Dict, Union

from ghkit.log import logger
from ghkit.messenger.dingtalk.dingtalk import DingTalkMessageType
from ghkit.messenger.dingtalk.message import build_message


class DingTalkCustomBotMessageSender:
    """钉钉自定义机器人消息发送"""

    def __init__(self, token: str, secret: str = None) -> None:
        """

        :param token:
        :param secret:
        """
        self.token = token
        self.secret = secret

    def send(
        self,
        message: Union[str, Dict],
        message_type: DingTalkMessageType = DingTalkMessageType.TEXT,
        timeout: int = 30,
    ) -> None:
        """
        同步发送消息
        :param message:
        :param message_type:
        :param timeout:
        :return:
        """
        msg = build_message(message, message_type)
        msg.send(token=self.token, secret=self.secret, timeout=timeout)
        logger.debug(f"Message sent: {msg}")

    async def async_send(
        self,
        message: Union[str, Dict],
        message_type: DingTalkMessageType = DingTalkMessageType.TEXT,
        timeout: int = 30,
    ) -> None:
        """
        异步发送消息
        :param message:
        :param message_type:
        :param timeout:
        :return:
        """
        msg = build_message(message, message_type)
        await msg.async_send(url=self.token, secret=self.secret, timeout=timeout)
        logger.debug(f"Message sent: msg:{msg}")
