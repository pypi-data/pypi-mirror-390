# FastAPI错误码定义
PARAM_ERROR = 10001  # 参数错误
NOT_FOUND = 10002  # 未找到
UNAUTHORIZED = 10003  # 未授权
FORBIDDEN = 10004  # 禁止访问
SERVER_ERROR = 10005  # 服务器错误


class BaseError(Exception):
    """基础异常类"""

    def __init__(self, message: str = None):
        self.message = message
        super().__init__(message)


class ParamError(BaseError):
    """参数错误"""

    pass


class NotFoundError(BaseError):
    """未找到错误"""

    pass


class UnauthorizedError(BaseError):
    """未授权错误"""

    pass


class ForbiddenError(BaseError):
    """禁止访问错误"""

    pass


class ServerError(BaseError):
    """服务器错误"""

    pass
