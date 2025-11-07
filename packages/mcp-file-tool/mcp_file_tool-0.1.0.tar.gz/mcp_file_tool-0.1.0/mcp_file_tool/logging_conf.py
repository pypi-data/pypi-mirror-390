import json
import logging
import os
from logging.handlers import RotatingFileHandler
from typing import Optional


class JsonFormatter(logging.Formatter):
    """JSON日志格式化器。

    将日志记录格式化为JSON，包含时间戳、级别、模块、消息及可选异常信息。
    """

    def format(self, record: logging.LogRecord) -> str:
        data = {
            "ts": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "func": record.funcName,
            "line": record.lineno,
            "msg": record.getMessage(),
        }
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
    - log_dir: 日志目录，默认使用当前项目中 `logs/`。
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

    # 文件滚动日志
    resolved_dir = log_dir or os.environ.get("MCP_FILE_TOOL_LOG_DIR", os.path.join(os.getcwd(), "logs"))
    _ensure_dir(resolved_dir)
    log_path = os.path.join(resolved_dir, "mcp_file_tool.log")
    file_handler = RotatingFileHandler(log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(root.level)
    root.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """获取命名日志记录器。

    参数:
    - name: 记录器名称。

    返回:
    - logging.Logger 对象。
    """

    return logging.getLogger(name)