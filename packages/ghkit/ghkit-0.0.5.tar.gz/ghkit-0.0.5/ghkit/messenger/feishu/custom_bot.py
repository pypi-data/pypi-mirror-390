from typing import Dict, Union

from ghkit.log import logger

from .feishu import FeishuBotType, FeishuMessageType
from .message import build_message


class FeishuCustomBot:
    """飞书自定义机器人消息发送"""

    def __init__(self, webhook_url: str, secret: str = None) -> None:
        """

        :param webhook_url:
        :param secret:
        """
        self.webhook_url = webhook_url
        self.secret = secret

    def send(
        self,
        message: Union[str, Dict],
        message_type: FeishuMessageType = FeishuMessageType.TEXT,
        timeout: int = 30,
    ) -> None:
        """
        同步发送消息
        :param message:
        :param message_type:
        :param timeout:
        :return:
        """
        msg = build_message(message, message_type, FeishuBotType.CUSTOM)
        msg.send(url=self.webhook_url, secret=self.secret, timeout=timeout)
        logger.debug(f"Message sent: {msg}")

    async def async_send(
        self,
        message: Union[str, Dict],
        message_type: FeishuMessageType = FeishuMessageType.TEXT,
        timeout: int = 30,
    ) -> None:
        """
        异步发送消息
        :param message:
        :param message_type:
        :param timeout:
        :return:
        """
        msg = build_message(message, message_type, FeishuBotType.CUSTOM)
        await msg.async_send(url=self.webhook_url, secret=self.secret, timeout=timeout)
        logger.debug(f"Message sent: msg:{msg}")
