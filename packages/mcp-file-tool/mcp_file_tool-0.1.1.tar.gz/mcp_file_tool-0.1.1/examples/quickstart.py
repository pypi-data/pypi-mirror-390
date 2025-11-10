"""快速开始示例：演示各工具的基本用法。

运行：
    python examples/quickstart.py
"""

import os
from pathlib import Path

# 将索引与日志定向到示例专用目录，避免污染仓库根目录
WORK_DIR = Path(__file__).resolve().parent / ".work"
os.makedirs(WORK_DIR, exist_ok=True)
os.environ.setdefault("MCP_FILE_TOOL_INDEX_DIR", str(WORK_DIR / ".mcp_index"))
os.environ.setdefault("MCP_FILE_TOOL_LOG_DIR", str(WORK_DIR / "logs"))

from mcp_file_tool.server import (
    tool_file_info,
    tool_read_bytes,
    tool_read_lines,
    tool_write_overwrite,
    tool_append,
    tool_insert,
    tool_build_line_index,
    tool_line_number_at_offset,
    tool_search_literal,
    tool_search_regex,
    tool_build_inverted_index,
    tool_search_index_term,
)


def _ensure_sample(path: Path, n: int = 1000) -> None:
    """确保示例文件存在；若不存在则生成固定内容。"""

    if not path.exists():
        with open(path, "wb") as f:
            for i in range(1, n + 1):
                f.write(f"line-{i:04d}\n".encode("utf-8"))


def main() -> None:
    """执行一次端到端示例调用。"""

    path = WORK_DIR / "sample.txt"
    _ensure_sample(path)
    print("INFO:", tool_file_info(path))
    print("READ BYTES:", tool_read_bytes(str(path), 0, 20)["data"])  
    print("READ LINES:", tool_read_lines(str(path), 10, 3)["lines"])  
    tool_write_overwrite(str(path), 0, "LINE-0")
    tool_write_overwrite(str(path), 0, "line-0")  # 还原
    tool_append(str(path), "extra-demo\n")
    lines = tool_read_lines(str(path), 1, 1)
    off = len(lines["lines"][0])
    tool_insert(str(path), off, "INS\n")
    print("LINE IDX:", tool_build_line_index(str(path), step=100))
    print("OFFSET->LINE:", tool_line_number_at_offset(str(path), 50))
    print("LITERAL:", tool_search_literal(str(path), "line-0099", max_results=1))
    print("REGEX:", tool_search_regex(str(path), r"line-0\d{2}0", max_results=1))
    tool_build_inverted_index(str(path), incremental=False)
    print("INV EXACT:", tool_search_index_term(str(path), term="line-0100"))
    print("INV PREFIX:", tool_search_index_term(str(path), term="line-01", prefix=True, limit=3))


if __name__ == "__main__":
    main()