import os
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
    - index_dir: 索引输出目录（存放行偏移索引等）。
    - log_dir: 日志目录。
    - log_level: 日志级别。
    - max_search_results: 搜索最大返回条数限制。
    - context_chars: 搜索命中周边返回的上下文字符数。
    """

    default_encoding: str = "utf-8"
    max_read_bytes: int = 4 * 1024 * 1024
    stream_buffer_bytes: int = 64 * 1024
    lock_timeout_sec: int = 10
    index_dir: str = ".mcp_index"
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
    - MCP_FILE_TOOL_INDEX_DIR
    - MCP_FILE_TOOL_LOG_DIR
    - MCP_FILE_TOOL_LOG_LEVEL
    - MCP_FILE_TOOL_MAX_SEARCH_RESULTS
    - MCP_FILE_TOOL_CONTEXT_CHARS
    """

    s = Settings()
    s.default_encoding = os.getenv("MCP_FILE_TOOL_ENCODING", s.default_encoding)
    s.max_read_bytes = int(os.getenv("MCP_FILE_TOOL_MAX_READ_BYTES", s.max_read_bytes))
    s.stream_buffer_bytes = int(os.getenv("MCP_FILE_TOOL_STREAM_BUFFER", s.stream_buffer_bytes))
    s.lock_timeout_sec = int(os.getenv("MCP_FILE_TOOL_LOCK_TIMEOUT", s.lock_timeout_sec))
    s.index_dir = os.getenv("MCP_FILE_TOOL_INDEX_DIR", s.index_dir)
    s.log_dir = os.getenv("MCP_FILE_TOOL_LOG_DIR", s.log_dir or os.path.join(os.getcwd(), "logs"))
    s.log_level = os.getenv("MCP_FILE_TOOL_LOG_LEVEL", s.log_level)
    s.max_search_results = int(os.getenv("MCP_FILE_TOOL_MAX_SEARCH_RESULTS", s.max_search_results))
    s.context_chars = int(os.getenv("MCP_FILE_TOOL_CONTEXT_CHARS", s.context_chars))
    return s


def ensure_dirs(settings: Settings) -> None:
    """确保必要目录存在。

    包括日志目录与索引目录。
    """

    os.makedirs(settings.log_dir or os.path.join(os.getcwd(), "logs"), exist_ok=True)
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