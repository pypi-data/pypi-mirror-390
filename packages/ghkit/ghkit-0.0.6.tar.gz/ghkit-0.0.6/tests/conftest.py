import os
import sys

import pytest

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 设置 pytest-asyncio 的事件循环作用域为函数级别
pytest_plugins = ("pytest_asyncio",)
pytest_asyncio_mode = "strict"
pytest_asyncio_default_fixture_loop_scope = "function"


# 在这里可以添加共享的 fixture
@pytest.fixture
def sample_data():
    return {"key": "value", "number": 42, "list": [1, 2, 3]}
