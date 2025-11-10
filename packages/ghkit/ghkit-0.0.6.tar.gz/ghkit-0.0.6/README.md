# ghkit

ghkit 是 "Grand Honor Kit" 的缩写，是一个 Python 项目通用工具包，提供了一系列常用的开发工具和功能模块。

## 功能特性

- 缓存系统：支持 Memory 和 Redis 缓存
- 数据库客户端：支持 MySQL 和 Redis
- 日志系统：基于 loguru 的通用日志模块
- 枚举工具：支持描述属性的增强枚举
- 消息通知：
  - 飞书机器人（支持文本、富文本、图片、卡片等消息）
  - 钉钉机器人（支持纯文本消息）
  - 邮件发送
- FastAPI 基础支持

## 安装

### 使用 pip（推荐）

```bash
pip install ghkit
```

### 使用 uv

```bash
# 安装 uv（如果还没有安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装 ghkit
uv pip install ghkit
```

### 开发安装

使用 uv 进行开发安装：

```bash
# 克隆项目
git clone <repository-url>
cd ghkit

# 安装项目及开发依赖
uv sync

# 或者只安装测试依赖
uv sync --extra test

# 或者安装所有可选依赖（包括 demo 依赖）
uv sync --all-extras
```

## 项目结构

```text
├── demo                        # 示例代码
├── docs                        # 文档
├── ghkit                       # 主要代码目录
│   ├── cache                   # 缓存模块
│   ├── database                # 数据库客户端
│   ├── enum                    # 枚举工具
│   ├── fastapi                 # FastAPI 基础支持
│   ├── log                     # 日志系统
│   └── messenger               # 消息通知
├── tests                       # 单元测试
├── CHANGELOG.md                # 版本更新日志
├── LICENSE                     # 开源协议
├── README.md                   # 项目说明
├── pyproject.toml              # 项目配置和依赖管理
└── uv.lock                     # uv 依赖锁定文件
```

## 版本历史

详细版本更新记录请查看 [CHANGELOG.md](CHANGELOG.md)

## 开发指南

### 运行测试

项目使用 pytest 作为测试框架。以下是运行测试的常用命令：

1. 安装测试依赖（使用 uv）：
```bash
uv sync --extra test
```

或者使用 pip：
```bash
pip install -e ".[test]"
```

2. 运行所有测试：
```bash
pytest
```

3. 运行测试并生成覆盖率报告：
```bash
pytest --cov=ghkit --cov-report=html
```

4. 运行特定测试文件：
```bash
pytest tests/test_log.py
```

5. 运行特定测试函数：
```bash
pytest tests/test_log.py::test_logger_creation
```

### 测试覆盖率报告

运行 `pytest --cov=ghkit --cov-report=html` 后：
- 在项目根目录生成 `htmlcov` 目录
- 打开 `htmlcov/index.html` 查看详细覆盖率报告
- 报告包含：
  - 总体覆盖率
  - 每个文件的覆盖率
  - 每个函数的覆盖率
  - 未覆盖的代码行

### 实用的 pytest 参数

- `-v`: 显示详细信息
- `-s`: 显示打印输出
- `-k "test_name"`: 只运行包含特定名称的测试
- `-x`: 遇到第一个失败就停止
- `--pdb`: 在测试失败时进入调试器

## 示例代码

查看 `demo` 目录获取更多使用示例：
- 枚举模块示例：`demo/enum/demo.py`
- FastAPI 示例：`demo/fastapi/demo.py`
- 飞书机器人示例：`demo/messenger/feishu/demo.py`


## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进这个项目。

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

