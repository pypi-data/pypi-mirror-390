from typing import List
from typing_extensions import TypedDict


class FileInfo(TypedDict):
    """文件信息结构。

    字段:
    - path: 文件路径
    - size: 文件大小（字节）
    - mtime: 修改时间（Unix 时间戳，秒）
    """

    path: str
    size: int
    mtime: int


class ReadBytesResult(TypedDict):
    """按字节读取返回结构。"""

    data: str
    offset: int
    bytes_read: int
    end_offset: int
    file_size: int


class ReadLinesResult(TypedDict):
    """按行读取返回结构。"""

    lines: List[str]
    start_line: int
    end_line: int
    total_lines: int
    start_offset: int
    end_offset: int


class WriteResult(TypedDict):
    """写入操作结果结构。"""

    path: str
    offset: int
    bytes_written: int
    end_offset: int


class InsertResult(TypedDict):
    """插入写入操作结果结构。"""

    path: str
    offset: int
    bytes_inserted: int
    new_size: int


class LineIndexBuildResult(TypedDict):
    """构建行索引的结果结构。"""

    path: str
    index_path: str
    entries: int
    step: int


class LineNumberResult(TypedDict):
    """偏移估算行号结果结构。"""

    line: int
    scanned_bytes: int
    from_checkpoint: bool


class RegexSearchMatch(TypedDict):
    """正则/字面量搜索单条命中结构。"""

    start_offset: int
    end_offset: int
    start_line: int
    end_line: int
    snippet: str


class RegexSearchResult(TypedDict):
    """正则搜索结果结构。"""

    matches: List[RegexSearchMatch]
    count: int


class LiteralSearchResult(TypedDict):
    """字面量搜索结果结构（与正则搜索相同形状）。"""

    matches: List[RegexSearchMatch]
    count: int


class IndexSearchMatch(TypedDict):
    """索引查询单条命中结构。"""

    term: str
    offset: int
    end_offset: int
    line: int
    snippet: str


class IndexSearchResult(TypedDict):
    """索引查询结果结构。"""

    matches: List[IndexSearchMatch]
    count: int


class BuildInvertedIndexResult(TypedDict):
    """构建倒排索引的结果结构。"""

    db_path: str
    mode: str
    indexed_bytes: int


__all__ = [
    "FileInfo",
    "ReadBytesResult",
    "ReadLinesResult",
    "WriteResult",
    "InsertResult",
    "LineIndexBuildResult",
    "LineNumberResult",
    "RegexSearchMatch",
    "RegexSearchResult",
    "LiteralSearchResult",
    "IndexSearchMatch",
    "IndexSearchResult",
    "BuildInvertedIndexResult",
]