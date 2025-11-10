"""控制台入口：启动 MCP STDIO 服务。

该模块作为 `console_scripts` 的入口点，用于在命令行运行：
    $ mcp-file-tool

改进：
- 捕获 `Ctrl+C`（SIGINT）触发的 `KeyboardInterrupt`，优雅退出并避免栈追踪噪声。
"""

from .server import mcp, settings
from .logging_conf import get_logger
import sys
import signal


def main() -> None:
    """启动 MCP 服务并使用 STDIO 作为传输层。

    说明：
    - 使用标准输入/输出（STDIO）与客户端（如 Trae/Claude Desktop）通信。
    - 默认日志目录：`~/.mft/logs/mcp_file_tool.log`（10MB滚动，保留5份）。
    - 捕获 `KeyboardInterrupt` 以优雅停止；捕获其它异常并记录详细错误栈。
    """

    logger = get_logger("main")
    transport = "stdio"
    # 启动前记录关键信息，便于使用者确认启动参数与日志位置
    logger.info("server_starting", extra={
        "transport": transport,
        "version": __import__("mcp_file_tool").__version__,
        "log_dir": settings.log_dir,
    })

    try:
        mcp.run(transport=transport)
    except KeyboardInterrupt:
        # 捕获一次 SIGINT 后，忽略后续 SIGINT，避免解释器关闭阶段被再次打断
        try:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
        except Exception:
            # 某些环境下可能不允许设置信号处理器，忽略即可
            pass
        # 将提示输出到 stderr，避免干扰 STDIO 传输协议的 stdout 通道
        sys.stderr.write("MCP 服务已停止（收到 Ctrl+C / SIGINT）\n")
        sys.stderr.flush()
        logger.info("server_stopped", extra={"reason": "KeyboardInterrupt"})
        # 正常退出码，避免异常栈打印
        sys.exit(0)
    except Exception:
        # 记录启动失败的详细原因（包含异常栈）
        logger.exception("server_startup_failed")
        # 使用非零退出码表明失败
        sys.exit(1)


if __name__ == "__main__":
    main()