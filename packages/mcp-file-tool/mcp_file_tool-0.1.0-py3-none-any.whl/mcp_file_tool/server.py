from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .config import init_runtime
from .chunkio import (
    read_bytes,
    read_lines,
    write_overwrite,
    append_chunk,
    insert_chunk,
    get_file_info,
    build_line_index,
    line_number_at_offset,
)
from .search import search_regex, search_literal
from .indexer import build_inverted_index, search_index_term
from .logging_conf import get_logger


# 初始化运行环境与日志
settings = init_runtime()
logger = get_logger("server")

# 创建 MCP 服务器
mcp = FastMCP("BigFile MCP Service")


@mcp.tool()
def tool_read_bytes(file_path: str, offset: int, length: int, encoding: str = settings.default_encoding) -> dict:
    """按字节分片读取文件内容。

    参数:
    - file_path: 文件路径
    - offset: 起始字节偏移（>=0）
    - length: 读取长度（>0）
    - encoding: 文本编码

    返回:
    - dict: 包含读取到的文本与元信息（偏移、长度等）。
    """

    return read_bytes(file_path, offset, length, encoding, max_read_bytes=settings.max_read_bytes)


@mcp.tool()
def tool_read_lines(file_path: str, start_line: int, num_lines: int, encoding: str = settings.default_encoding) -> dict:
    """按行分片读取文件内容。

    参数:
    - file_path: 文件路径
    - start_line: 起始行（>=1）
    - num_lines: 读取行数（>0）
    - encoding: 文本编码

    返回:
    - dict: 包含读取的行列表与行/偏移信息。
    """

    return read_lines(file_path, start_line, num_lines, encoding, stream_buffer_bytes=settings.stream_buffer_bytes)


@mcp.tool()
def tool_write_overwrite(file_path: str, offset: int, data: str, encoding: str = settings.default_encoding) -> dict:
    """覆盖写入：从指定字节偏移开始写入文本数据。

    参数:
    - file_path: 文件路径
    - offset: 写入起始字节偏移
    - data: 文本数据
    - encoding: 文本编码

    返回:
    - dict: 写入结果信息（字节数、末尾偏移）。
    """

    return write_overwrite(file_path, offset, data, encoding, lock_timeout_sec=settings.lock_timeout_sec)


@mcp.tool()
def tool_append(file_path: str, data: str, encoding: str = settings.default_encoding) -> dict:
    """追加写入：在文件末尾追加文本数据。

    参数:
    - file_path: 文件路径
    - data: 文本数据
    - encoding: 文本编码

    返回:
    - dict: 写入结果信息（追加起始偏移、末尾偏移）。
    """

    return append_chunk(file_path, data, encoding, lock_timeout_sec=settings.lock_timeout_sec)


@mcp.tool()
def tool_insert(file_path: str, offset: int, data: str, encoding: str = settings.default_encoding, temp_dir: Optional[str] = None) -> dict:
    """插入写入：在指定字节偏移处插入文本数据（原子替换）。

    参数:
    - file_path: 文件路径
    - offset: 插入偏移
    - data: 文本数据
    - encoding: 文本编码
    - temp_dir: 临时目录（可选）

    返回:
    - dict: 插入结果信息（新文件大小等）。
    """

    td = temp_dir
    return insert_chunk(file_path, offset, data, encoding, td, stream_buffer_bytes=settings.stream_buffer_bytes, lock_timeout_sec=settings.lock_timeout_sec)


@mcp.tool()
def tool_file_info(file_path: str) -> dict:
    """获取文件基本信息（路径、大小、修改时间）。"""

    return get_file_info(file_path)


@mcp.tool()
def tool_build_line_index(file_path: str, step: int = 1000) -> dict:
    """构建行偏移索引（每 step 行记录一次字节偏移）。

    参数:
    - file_path: 目标文件
    - step: 间隔行数

    返回:
    - dict: 索引文件路径与条目数。
    """

    return build_line_index(file_path, step=step, encoding=settings.default_encoding, stream_buffer_bytes=settings.stream_buffer_bytes, index_dir=settings.index_dir)


@mcp.tool()
def tool_search_regex(
    file_path: str,
    pattern: str,
    encoding: str = settings.default_encoding,
    start_offset: int = 0,
    end_offset: Optional[int] = None,
    max_results: int = 200,
    context_chars: int = settings.context_chars,
    flags: Optional[str] = None,
) -> dict:
    """流式正则搜索大文件，返回命中偏移、近似行号及上下文。

    参数详见返回的字典说明。
    """

    return search_regex(
        file_path,
        pattern,
        encoding=encoding,
        start_offset=start_offset,
        end_offset=end_offset,
        max_results=min(max_results, settings.max_search_results),
        context_chars=context_chars,
        stream_buffer_bytes=settings.stream_buffer_bytes,
        flags=flags,
    )


@mcp.tool()
def tool_search_literal(
    file_path: str,
    query: str,
    encoding: str = settings.default_encoding,
    start_offset: int = 0,
    end_offset: Optional[int] = None,
    max_results: int = 200,
    context_chars: int = settings.context_chars,
    case_sensitive: bool = True,
) -> dict:
    """流式字面量搜索大文件，返回命中偏移、近似行号及上下文。"""

    return search_literal(
        file_path,
        query,
        encoding=encoding,
        start_offset=start_offset,
        end_offset=end_offset,
        max_results=min(max_results, settings.max_search_results),
        context_chars=context_chars,
        stream_buffer_bytes=settings.stream_buffer_bytes,
        case_sensitive=case_sensitive,
    )


logger.info("server_initialized", extra={"settings": settings.__dict__})


@mcp.tool()
def tool_build_inverted_index(
    file_path: str,
    incremental: bool = True,
    token_pattern: str = r"[\w\-]+",
    lower: bool = True,
) -> dict:
    """构建或增量更新倒排索引（SQLite存储）。

    仅支持“末尾追加”的增量更新；若检测到非追加修改则自动触发全量重建。
    """

    return build_inverted_index(
        file_path,
        incremental=incremental,
        encoding=settings.default_encoding,
        token_pattern=token_pattern,
        lower=lower,
        stream_buffer_bytes=settings.stream_buffer_bytes,
        index_dir=settings.index_dir,
    )


@mcp.tool()
def tool_search_index_term(
    file_path: str,
    term: str,
    prefix: bool = False,
    limit: int = 200,
    context_chars: int = settings.context_chars,
) -> dict:
    """使用倒排索引查询词项，返回命中偏移与上下文片段。"""

    return search_index_term(
        file_path,
        term,
        prefix=prefix,
        limit=min(limit, settings.max_search_results),
        context_chars=context_chars,
        encoding=settings.default_encoding,
        index_dir=settings.index_dir,
    )


@mcp.tool()
def tool_line_number_at_offset(file_path: str, offset: int) -> dict:
    """根据字节偏移估算行号，若存在索引则快速定位。"""

    return line_number_at_offset(
        file_path,
        offset,
        index_dir=settings.index_dir,
        stream_buffer_bytes=settings.stream_buffer_bytes,
    )