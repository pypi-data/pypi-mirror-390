"""示例：Excel → CSV → MCP 逐行读写

运行：
    python examples/excel_to_mcp_csv_demo.py

说明：
- Excel（xlsx/xls）为二进制格式，无法直接按“行”读取；建议先转为 CSV。
- 本示例会复制仓库内示例 CSV 到本地工作目录，不修改原始文件。
"""

import os
import io
import csv
import shutil
from pathlib import Path
from typing import List, Optional

# 将索引与日志定向到示例专用目录，避免污染仓库根目录
WORK_DIR = Path(__file__).resolve().parent / ".work"
os.makedirs(WORK_DIR, exist_ok=True)
os.environ.setdefault("MCP_FILE_TOOL_INDEX_DIR", str(WORK_DIR / ".mcp_index"))
os.environ.setdefault("MCP_FILE_TOOL_LOG_DIR", str(WORK_DIR / "logs"))

from mcp_file_tool.server import (
    tool_file_info,
    tool_read_lines,
    tool_append,
    tool_insert,
    tool_write_overwrite,
    tool_build_line_index,
)


def convert_excel_to_csv(xlsx_path: str, csv_path: str, sheet_name: Optional[str] = None) -> None:
    """将 Excel 文件转换为 CSV。

    参数:
    - xlsx_path: Excel 文件路径（.xlsx/.xls）
    - csv_path: 输出 CSV 路径
    - sheet_name: 指定工作表名；None 表示使用默认第一个工作表

    说明:
    - 仅在需要时导入 pandas/openpyxl；若未安装且需要转换，将提示安装。
    """

    try:
        import pandas as pd  # type: ignore
    except Exception as e:
        raise RuntimeError(
            "需要 pandas 才能转换 Excel→CSV，请先安装：pip install pandas openpyxl"
        ) from e

    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, engine=None)
    if isinstance(df, dict):
        # 多表时，选择第一个表或根据需求合并
        first_key = next(iter(df.keys()))
        df = df[first_key]
    df.to_csv(csv_path, index=False)


def format_csv_rows(rows: List[List[str]]) -> str:
    """将二维数组行安全地格式化为 CSV 文本片段。

    参数:
    - rows: 每条记录为一个字符串列表（列）

    返回:
    - 规范的 CSV 文本（包含换行），保证包含逗号/引号/换行等特殊字符时仍合法。
    """

    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\n")
    for r in rows:
        writer.writerow(r)
    return buf.getvalue()


def read_csv_in_chunks(csv_path: str, start_line: int = 1, chunk_size: int = 50) -> None:
    """按行分片读取 CSV 文件并处理。

    参数:
    - csv_path: CSV 文件路径
    - start_line: 起始行号（>=1）
    - chunk_size: 每次读取的行数

    说明:
    - 使用 MCP 的 tool_read_lines 返回 lines、start_offset/end_offset、end_line/total_lines。
    - 逐块推进直到读取完整文件。
    """

    info = tool_file_info(file_path=csv_path)
    print(f"文件大小: {info['size']} 字节")

    current = start_line
    while True:
        res = tool_read_lines(file_path=csv_path, start_line=current, num_lines=chunk_size)
        lines = res["lines"]
        if not lines:
            print("读取结束。")
            break

        # 在此处理每行内容（示例中直接打印前 2 行）
        for i, line in enumerate(lines[:2], start=0):
            print(f"[样例] 行 {res['start_line'] + i}: {line.rstrip()}")

        current = res["end_line"] + 1
        if res["end_line"] >= res["total_lines"]:
            print("已读取到文件末尾。")
            break


def append_rows(csv_path: str, rows: List[List[str]]) -> None:
    """在 CSV 文件末尾追加多行记录。

    参数:
    - csv_path: 目标 CSV 文件
    - rows: 追加的记录列表（每条为列数组）

    说明:
    - 使用 csv.writer 确保转义与引号正确。
    - 通过 MCP 的 tool_append 原子追加写入。
    """

    data = format_csv_rows(rows)
    r = tool_append(file_path=csv_path, data=data)
    print(f"已追加 {r['bytes_written']} 字节到末尾，末尾偏移 {r['end_offset']}。")


def insert_rows_at_line(csv_path: str, line_no: int, rows: List[List[str]]) -> None:
    """在指定行号之前插入多行 CSV 记录。

    参数:
    - csv_path: 目标 CSV 文件
    - line_no: 在该行“之前”插入（例如 2 表示在第 2 行前插入）
    - rows: 待插入的记录列表

    实现:
    - 通过 tool_read_lines 定位目标行的起始字节偏移（start_offset）。
    - 使用 tool_insert 在该偏移处执行安全插入（临时文件原子替换）。

    注意:
    - 确保插入的数据以换行结尾；format_csv_rows 已按行输出并带换行。
    """

    # 为加速后续按行定位，可先构建行索引（可选）
    tool_build_line_index(file_path=csv_path, step=1000)

    # 定位目标行的起始偏移
    res = tool_read_lines(file_path=csv_path, start_line=line_no, num_lines=1)
    start_offset = res["start_offset"]
    data = format_csv_rows(rows)
    ins = tool_insert(file_path=csv_path, offset=start_offset, data=data)
    print(f"已在偏移 {ins['offset']} 处插入 {ins['bytes_inserted']} 字节，新文件大小 {ins['new_size']}。")


def overwrite_at_offset(csv_path: str, offset: int, text: str) -> None:
    """在指定字节偏移处覆盖写入文本（高级用法，慎用）。

    参数:
    - csv_path: 目标 CSV 文件
    - offset: 字节偏移（>=0）
    - text: 要写入的文本（原样覆盖）

    使用场景:
    - 修补某一小段已知偏移的文本。
    - 注意此操作不会自动对齐行边界，可能破坏 CSV 格式；一般优先用 insert/append。
    """

    r = tool_write_overwrite(file_path=csv_path, offset=offset, text=text)
    print(f"覆盖写入 {r['bytes_written']} 字节，末尾偏移 {r['end_offset']}。")


def main() -> None:
    """演示完整流程：Excel → CSV → MCP 逐行读写。

    - 若工作目录存在 sample.xlsx，则优先转换为 CSV 演示。
    - 否则复制仓库 examples/mcp_large_test.csv 到工作目录使用。
    - 不会修改仓库内原始示例文件。
    """

    xlsx = WORK_DIR / "sample.xlsx"
    src_csv = Path(__file__).resolve().parent / "mcp_large_test.csv"
    demo_csv = WORK_DIR / "mcp_demo.csv"

    if xlsx.exists():
        convert_excel_to_csv(str(xlsx), str(demo_csv), sheet_name=None)
        print(f"已转换 Excel 到 CSV: {demo_csv}")
    else:
        if src_csv.exists():
            shutil.copyfile(src_csv, demo_csv)
            print(f"已复制示例 CSV 到工作目录: {demo_csv}")
        else:
            print("未找到示例 CSV，退出。")
            return

    # 1) 逐行读取（每次 50 行）
    read_csv_in_chunks(str(demo_csv), start_line=1, chunk_size=50)

    # 2) 追加两行
    append_rows(str(demo_csv), [["new_id_1", "foo,bar", "100"], ["new_id_2", "baz\"qux", "200"]])

    # 3) 在第 2 行前插入一行
    insert_rows_at_line(str(demo_csv), 2, [["inserted_id", "hello\nworld", "999"]])

    # 4) 若确有需要，按偏移覆盖写入（示例：从文件头覆盖写入一段注释）
    overwrite_at_offset(str(demo_csv), 0, "# header note (use insert for rows)\n")


if __name__ == "__main__":
    main()