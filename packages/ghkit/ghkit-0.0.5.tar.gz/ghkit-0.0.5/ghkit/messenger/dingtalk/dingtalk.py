import base64
import hashlib
import hmac
from urllib.parse import quote_plus

from ghkit.enum import GEnum


class DingTalkMessageType(GEnum):
    """
    钉钉消息类型枚举
    """

    TEXT = "text"  # 文本


def gen_sign(timestamp: int, secret: str):
    """生成签名"""

    secret_enc = secret.encode("utf-8")
    string_to_sign = "{}\n{}".format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode("utf-8")
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = quote_plus(base64.b64encode(hmac_code))

    return sign
