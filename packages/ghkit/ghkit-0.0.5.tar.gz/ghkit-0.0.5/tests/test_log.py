from ghkit.log import LOG, setup_logging


def test_logger_basic():
    """测试基本日志功能"""
    # 测试各个日志级别的方法是否存在
    assert hasattr(LOG, "debug")
    assert hasattr(LOG, "info")
    assert hasattr(LOG, "warning")
    assert hasattr(LOG, "error")
    assert hasattr(LOG, "critical")


def test_logger_level():
    """测试日志级别设置"""
    # 测试设置日志级别
    LOG.level("INFO")
    assert LOG.level("INFO").name == "INFO"


def test_logger_output():
    """测试日志输出配置"""
    # 测试添加文件输出
    LOG.add("test.log", rotation="100 MB")
    LOG.info("测试日志输出")

    # 测试日志记录
    LOG.info("这是一条测试日志")
    LOG.error("这是一条错误日志")


def test_setup_logging():
    """测试日志拦截器设置"""
    # 测试设置日志拦截器
    setup_logging()
    # 验证是否成功设置（这里主要是验证函数可以正常执行）
    assert True
