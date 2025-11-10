class MessengerError(Exception):
    """通用消息错误"""


class AccessTokenError(MessengerError):
    """获取鉴权凭证失败"""


class LoginError(MessengerError):
    """登录失败"""


class SendError(MessengerError):
    """发送失败"""


class MessageTypeError(MessengerError):
    """消息格式错误"""
