import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional
from pathlib import Path


class JsonFormatter(logging.Formatter):
    """JSON日志格式化器。

    将日志记录格式化为 JSON。除基本字段外，还自动包含：
    - 进程 ID（process）与线程名（threadName）
    - 通过 `logger.info(..., extra={...})` 传入的扩展字段，置于 `extra` 中
    - 异常信息（exc_info）当存在时
    """

    def format(self, record: logging.LogRecord) -> str:
        data = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "process": getattr(record, "process", None),
            "thread": getattr(record, "threadName", None),
            "msg": record.getMessage(),
        }

        # 收集 extra 字段（排除标准属性）
        standard_keys = {
            "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
            "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "created", "msecs", "relativeCreated", "thread", "threadName", "processName",
            "process"
        }
        extras: dict = {}
        for k, v in record.__dict__.items():
            if k not in standard_keys and k not in data and not k.startswith("_"):
                extras[k] = v
        if extras:
            data["extra"] = extras

        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(data, ensure_ascii=False)


def _ensure_dir(path: str) -> None:
    """确保目录存在。

    如果目录不存在则创建。
    """

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def setup_logging(log_dir: Optional[str] = None, level: str = "INFO") -> None:
    """初始化全局日志配置。

    参数:
    - log_dir: 日志目录，默认使用用户家目录下的 `~/.mft/logs`。
    - level: 日志级别，默认为 "INFO"。
    """

    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    formatter = JsonFormatter()

    # 控制台（stderr）
    console = logging.StreamHandler()
    console.setFormatter(formatter)
    console.setLevel(root.level)
    root.addHandler(console)

    # 文件滚动日志，默认写入 ~/.mft/logs/mcp_file_tool.log
    default_dir = os.environ.get("MCP_FILE_TOOL_LOG_DIR") or os.path.join(str(Path.home()), ".mft", "logs")
    resolved_dir = log_dir or default_dir
    _ensure_dir(resolved_dir)
    log_path = os.path.join(resolved_dir, "mcp_file_tool.log")
    file_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(root.level)
    root.addHandler(file_handler)

    # 初始化完成日志，便于用户确认日志位置与级别
    root.info("logging_initialized", extra={"log_dir": resolved_dir, "log_path": log_path, "level": logging.getLevelName(root.level)})


def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器。

    参数:
    - name: 记录器名称。

    返回:
    - logging.Logger 对象。
    """

    return logging.getLogger(name)