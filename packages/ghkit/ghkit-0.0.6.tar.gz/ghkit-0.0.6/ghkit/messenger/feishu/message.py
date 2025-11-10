import json
import time
import uuid
from typing import Dict, Union

import httpx
import requests

from ghkit.messenger import Message
from ghkit.messenger.error import MessageTypeError
from ghkit.messenger.feishu import FeishuBotType, FeishuMessageType, gen_sign


class FeishuMessage(Message):

    def handle_app_bot_msg(self, receive_id: str):
        """处理应用机器人消息"""
        if receive_id:
            self.msg_data["receive_id"] = receive_id
            self.msg_data["uuid"] = uuid.uuid4().hex
            self.msg_data["content"] = json.dumps(self.msg_data["content"])

    def handle_secret(self, secret):
        if secret:
            timestamp = round(time.time())
            sign = gen_sign(timestamp, secret)
            self.msg_data["sign"] = sign
            self.msg_data["timestamp"] = timestamp

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
        try:
            self.handle_secret(secret)
            self.handle_app_bot_msg(receive_id)
            response = requests.post(url=url, json=self.msg_data, timeout=timeout, **kwargs)
            self.handler_response(response)
        except Exception as e:
            self.handle_send_error(e)

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
        try:
            self.handle_secret(secret)
            self.handle_app_bot_msg(receive_id)
            async with httpx.AsyncClient() as client:
                response = await client.post(url=url, json=self.msg_data, timeout=timeout, **kwargs)
                self.handler_response(response)
        except Exception as e:
            self.handle_send_error(e)

    def __repr__(self):
        return json.dumps(self.msg_data, ensure_ascii=False)


class TextMessage(FeishuMessage):
    """文本消息"""

    def __init__(self, text: str) -> None:
        msg_data = {"msg_type": "text", "content": {"text": text}}
        super().__init__(msg_data)


class PostMessage(FeishuMessage):
    """富文本消息"""

    def __init__(self, content: Dict, bot_type: FeishuBotType) -> None:
        if bot_type == FeishuBotType.CUSTOM:
            content = {"post": content}
        msg_data = {"msg_type": "post", "content": content}
        super().__init__(msg_data)


class ImageMessage(FeishuMessage):
    """图片消息"""

    def __init__(self, image_key: str) -> None:
        msg_data = {"msg_type": "image", "content": {"image_key": image_key}}
        super().__init__(msg_data)


class ShareChatMessage(FeishuMessage):
    """群名片消息"""

    def __init__(self, chat_id: str, bot_type: FeishuBotType) -> None:
        key = "share_chat_id" if bot_type == FeishuBotType.CUSTOM else "chat_id"
        msg_data = {"msg_type": "share_chat", "content": {key: chat_id}}
        super().__init__(msg_data)


class CardMessage(FeishuMessage):
    """卡片消息"""

    def __init__(self, card: Dict, bot_type: FeishuBotType) -> None:
        key = "card" if bot_type == FeishuBotType.CUSTOM else "content"
        msg_data = {"msg_type": "interactive", key: card}
        super().__init__(msg_data)


def build_message(
    message: Union[str, Dict], message_type: FeishuMessageType, bot_type: FeishuBotType
) -> Message:
    """
    构建消息
    :param message:
    :param message_type:
    :param bot_type:
    :return:
    """
    # 根据消息类型构建消息对象
    if message_type == FeishuMessageType.TEXT:
        return TextMessage(message)
    elif message_type == FeishuMessageType.POST:
        return PostMessage(message, bot_type)
    elif message_type == FeishuMessageType.IMAGE:
        return ImageMessage(message)
    elif message_type == FeishuMessageType.SHARE_CHAT:
        return ShareChatMessage(message, bot_type)
    elif message_type == FeishuMessageType.INTERACTIVE:
        return CardMessage(message, bot_type)
    else:
        raise MessageTypeError
