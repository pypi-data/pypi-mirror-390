import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

from .logging_conf import setup_logging, get_logger


@dataclass
class Settings:
    """服务配置项。

    - default_encoding: 默认文本编码。
    - max_read_bytes: 单次读取的最大字节数上限（保护上下文）。
    - stream_buffer_bytes: 流式读取缓冲区大小。
    - lock_timeout_sec: 文件写入锁超时时间。
    - runtime_dir: 运行时根目录（默认 `~/.mft`）。
    - index_dir: 索引输出目录（默认派生自 runtime_dir 为 `~/.mft/.mcp_index`）。
    - log_dir: 日志目录（默认派生自 runtime_dir 为 `~/.mft/logs`）。
    - log_level: 日志级别。
    - max_search_results: 搜索最大返回条数限制。
    - context_chars: 搜索命中周边返回的上下文字符数。
    """

    default_encoding: str = "utf-8"
    max_read_bytes: int = 4 * 1024 * 1024
    stream_buffer_bytes: int = 64 * 1024
    lock_timeout_sec: int = 10
    runtime_dir: Optional[str] = None
    index_dir: Optional[str] = None
    log_dir: Optional[str] = None
    log_level: str = "INFO"
    max_search_results: int = 200
    context_chars: int = 96


def load_settings() -> Settings:
    """从环境变量加载配置。

    支持的环境变量：
    - MCP_FILE_TOOL_ENCODING
    - MCP_FILE_TOOL_MAX_READ_BYTES
    - MCP_FILE_TOOL_STREAM_BUFFER
    - MCP_FILE_TOOL_LOCK_TIMEOUT
    - MCP_FILE_TOOL_RUNTIME_DIR（新增，统一运行时根目录，默认 `~/.mft`）
    - MCP_FILE_TOOL_INDEX_DIR（优先级高于 runtime_dir 派生值）
    - MCP_FILE_TOOL_LOG_DIR（优先级高于 runtime_dir 派生值）
    - MCP_FILE_TOOL_LOG_LEVEL
    - MCP_FILE_TOOL_MAX_SEARCH_RESULTS
    - MCP_FILE_TOOL_CONTEXT_CHARS
    """

    s = Settings()
    s.default_encoding = os.getenv("MCP_FILE_TOOL_ENCODING", s.default_encoding)
    s.max_read_bytes = int(os.getenv("MCP_FILE_TOOL_MAX_READ_BYTES", s.max_read_bytes))
    s.stream_buffer_bytes = int(os.getenv("MCP_FILE_TOOL_STREAM_BUFFER", s.stream_buffer_bytes))
    s.lock_timeout_sec = int(os.getenv("MCP_FILE_TOOL_LOCK_TIMEOUT", s.lock_timeout_sec))
    # 统一运行时目录到用户家目录下的 ~/.mft
    default_runtime_dir = os.path.join(str(Path.home()), ".mft")
    default_index_dir = os.path.join(default_runtime_dir, ".mcp_index")
    # 统一运行时目录（可通过 MCP_FILE_TOOL_RUNTIME_DIR 覆盖）
    default_runtime_dir = os.path.join(str(Path.home()), ".mft")
    s.runtime_dir = os.getenv("MCP_FILE_TOOL_RUNTIME_DIR", s.runtime_dir or default_runtime_dir)
    # 由 runtime_dir 派生默认索引与日志目录；若显式指定 INDEX_DIR/LOG_DIR，则优先生效
    default_index_dir = os.path.join(s.runtime_dir, ".mcp_index")
    s.index_dir = os.getenv("MCP_FILE_TOOL_INDEX_DIR", s.index_dir or default_index_dir)
    # 日志目录默认放置在运行时目录下的 `logs` 子目录
    s.log_dir = os.getenv("MCP_FILE_TOOL_LOG_DIR", s.log_dir or os.path.join(s.runtime_dir, "logs"))
    s.log_level = os.getenv("MCP_FILE_TOOL_LOG_LEVEL", s.log_level)
    s.max_search_results = int(os.getenv("MCP_FILE_TOOL_MAX_SEARCH_RESULTS", s.max_search_results))
    s.context_chars = int(os.getenv("MCP_FILE_TOOL_CONTEXT_CHARS", s.context_chars))
    return s


def ensure_dirs(settings: Settings) -> None:
    """确保必要目录存在。

    包括运行时根目录、日志目录与索引目录。默认运行时根目录为 `~/.mft`，索引目录为
    `~/.mft/.mcp_index`，日志目录为 `~/.mft/logs`。
    """

    runtime_dir = settings.runtime_dir or os.path.join(str(Path.home()), ".mft")
    os.makedirs(runtime_dir, exist_ok=True)
    os.makedirs(settings.log_dir or runtime_dir, exist_ok=True)
    os.makedirs(settings.index_dir, exist_ok=True)


def init_runtime() -> Settings:
    """初始化运行环境与日志系统。

    返回:
    - Settings 对象。
    """

    s = load_settings()
    ensure_dirs(s)
    setup_logging(s.log_dir, s.log_level)
    logger = get_logger("config")
    logger.info("settings_loaded", extra={"settings": s.__dict__})
    return s