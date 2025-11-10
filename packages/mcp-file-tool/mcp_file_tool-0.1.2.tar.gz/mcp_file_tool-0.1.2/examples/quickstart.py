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
    print("INFO:", tool_file_info(file_path=str(path)))
    print("READ BYTES:", tool_read_bytes(file_path=str(path), offset=0, length=20)["data"])  
    print("READ LINES:", tool_read_lines(file_path=str(path), start_line=10, num_lines=3)["lines"])  
    tool_write_overwrite(file_path=str(path), offset=0, data="LINE-0")
    tool_write_overwrite(file_path=str(path), offset=0, data="line-0")  # 还原
    tool_append(file_path=str(path), data="extra-demo\n")
    lines = tool_read_lines(file_path=str(path), start_line=1, num_lines=1)
    off = len(lines["lines"][0])
    tool_insert(file_path=str(path), offset=off, data="INS\n")
    print("LINE IDX:", tool_build_line_index(file_path=str(path), step=100))
    print("OFFSET->LINE:", tool_line_number_at_offset(file_path=str(path), offset=50))
    print("LITERAL:", tool_search_literal(file_path=str(path), query="line-0099", max_results=1))
    print("REGEX:", tool_search_regex(file_path=str(path), pattern=r"line-0\d{2}0", max_results=1))
    tool_build_inverted_index(file_path=str(path), incremental=False)
    print("INV EXACT:", tool_search_index_term(file_path=str(path), term="line-0100"))
    print("INV PREFIX:", tool_search_index_term(file_path=str(path), term="line-01", prefix=True, limit=3))


if __name__ == "__main__":
    main()