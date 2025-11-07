"""控制台入口：启动 MCP STDIO 服务。

该模块作为 `console_scripts` 的入口点，用于在命令行运行：
    $ mcp-file-tool
"""

from .server import mcp


def main() -> None:
    """启动 MCP 服务并使用 STDIO 作为传输层。

    说明：
    - 使用标准输入/输出（STDIO）与客户端（如 Trae/Claude Desktop）通信。
    - 日志输出到控制台与 `logs/mcp_file_tool.log`（旋转）。
    """

    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()