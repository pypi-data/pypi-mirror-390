from typing import TypeVar

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ghkit.log import setup_logging

from .error import (
    FORBIDDEN,
    NOT_FOUND,
    PARAM_ERROR,
    SERVER_ERROR,
    UNAUTHORIZED,
    ForbiddenError,
    NotFoundError,
    ParamError,
    ServerError,
    UnauthorizedError,
)
from .filter import FilterParams
from .paginate import PageParams, paginate

__all__ = [
    "error_handler",
    "create_app",
    "paginate",
    "PageParams",
    "FilterParams",
    # 错误相关
    "PARAM_ERROR",
    "NOT_FOUND",
    "UNAUTHORIZED",
    "FORBIDDEN",
    "SERVER_ERROR",
    "ParamError",
    "NotFoundError",
    "UnauthorizedError",
    "ForbiddenError",
    "ServerError",
]

T = TypeVar("T")


def error_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """错误处理器"""
    return JSONResponse(
        status_code=exc.status_code, content={"code": exc.status_code, "message": exc.detail}
    )


def create_app(title: str = "GHKit API", version: str = "0.1.0") -> FastAPI:
    """
    创建FastAPI应用
    :param title: 应用标题
    :param version: 应用版本
    :return: FastAPI应用实例
    """
    # 设置日志
    setup_logging()

    # 创建FastAPI应用
    app = FastAPI(
        title=title,
        version=version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 注册路由
    @app.get("/health")
    async def health_check():
        """健康检查接口"""
        return {"status": "ok"}

    # 错误处理
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        """参数验证错误处理"""
        return JSONResponse(
            status_code=400,
            content={"code": PARAM_ERROR, "msg": str(exc)},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request, exc):
        """未找到错误处理"""
        return JSONResponse(
            status_code=404,
            content={"code": NOT_FOUND, "msg": str(exc)},
        )

    @app.exception_handler(ParamError)
    async def param_error_handler(request, exc):
        """参数错误处理"""
        return JSONResponse(
            status_code=400,
            content={"code": PARAM_ERROR, "msg": str(exc)},
        )

    @app.exception_handler(UnauthorizedError)
    async def unauthorized_error_handler(request, exc):
        """未授权错误处理"""
        return JSONResponse(
            status_code=401,
            content={"code": UNAUTHORIZED, "msg": str(exc)},
        )

    @app.exception_handler(ForbiddenError)
    async def forbidden_error_handler(request, exc):
        """禁止访问错误处理"""
        return JSONResponse(
            status_code=403,
            content={"code": FORBIDDEN, "msg": str(exc)},
        )

    @app.exception_handler(ServerError)
    async def server_error_handler(request, exc):
        """服务器错误处理"""
        return JSONResponse(
            status_code=500,
            content={"code": SERVER_ERROR, "msg": str(exc)},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        """HTTP异常处理"""
        if exc.status_code == 404:
            return JSONResponse(
                status_code=404,
                content={"code": NOT_FOUND, "msg": "Not Found"},
            )
        elif exc.status_code == 401:
            return JSONResponse(
                status_code=401,
                content={"code": UNAUTHORIZED, "msg": "Unauthorized"},
            )
        elif exc.status_code == 403:
            return JSONResponse(
                status_code=403,
                content={"code": FORBIDDEN, "msg": "Forbidden"},
            )
        else:
            return JSONResponse(
                status_code=500,
                content={"code": SERVER_ERROR, "msg": "Internal Server Error"},
            )

    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """通用异常处理"""
        return JSONResponse(
            status_code=500,
            content={"code": SERVER_ERROR, "msg": "Internal Server Error"},
        )

    return app
