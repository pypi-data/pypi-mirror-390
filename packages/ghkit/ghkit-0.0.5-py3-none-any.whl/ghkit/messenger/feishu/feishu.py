import base64
import hashlib
import hmac
from enum import auto

from ghkit.enum import GEnum


class FeishuReceiveType(GEnum):
    """消息接收者id类型"""

    OPEN_ID = "open_id"  # 标识一个用户在某个应用中的身份
    USER_ID = "user_id"  # 标识一个用户在某个租户内的身份
    UNION_ID = "union_id"  # 标识一个用户在某个应用开发商下的身份
    EMAIL = "email"  # 以用户的真实邮箱来标识用户
    CHAT_ID = "chat_id"  # 以群ID来标识群聊


class FeishuMessageType(GEnum):
    """
    飞书消息类型枚举
    文档：https://open.feishu.cn/document/server-docs/im-v1/message-content-description/create_json#3c92befd
    """

    TEXT = "text"  # 文本
    POST = "post"  # 富文本
    IMAGE = "image"  # 图片
    SHARE_CHAT = "share_chat"  # 分享群名片
    SHARE_USER = "share_user"  # 分享个人名片
    INTERACTIVE = "interactive"  # 消息卡片
    AUDIO = "audio"  # 音频
    VIDEO = "video"  # 视频
    FILE = "file"  # 文件
    STICKER = "sticker"  # 表情包


class FeishuBotType(GEnum):
    """
    飞书机器人类型
    """

    CUSTOM = auto()
    APPLICATION = auto()


def gen_sign(timestamp: int, secret: str):
    """生成签名"""

    # 拼接timestamp和secret
    string_to_sign = "{}\n{}".format(timestamp, secret)
    hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
    # 对结果进行base64处理
    sign = base64.b64encode(hmac_code).decode("utf-8")
    return sign
