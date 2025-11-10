import logging

from loguru import logger


class InterceptHandler(logging.Handler):
    """拦截标准 logging 记录并重定向到 loguru"""

    def emit(self, record):
        loguru_level = record.levelname.upper()
        if loguru_level == "WARN":
            loguru_level = "WARNING"
        logger_opt = LOG.opt(depth=6, exception=record.exc_info)
        logger_opt.log(loguru_level, record.getMessage())


def setup_logging(level: int = logging.DEBUG):
    """替换 FastAPI & Uvicorn & Tortoise-ORM 的 logging 配置"""
    logging.basicConfig(handlers=[InterceptHandler()], level=level)


LOG = logger
