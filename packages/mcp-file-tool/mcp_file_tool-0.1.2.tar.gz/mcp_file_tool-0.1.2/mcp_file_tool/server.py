from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .config import init_runtime
from .chunkio import (
    read_bytes,
    read_lines,
    read_last_lines,
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
from .types import (
    FileInfo,
    ReadBytesResult,
    ReadLinesResult,
    WriteResult,
    InsertResult,
    LineIndexBuildResult,
    LineNumberResult,
    RegexSearchResult,
    LiteralSearchResult,
    BuildInvertedIndexResult,
    IndexSearchResult,
)


# 初始化运行环境与日志
settings = init_runtime()
logger = get_logger("server")

# 创建 MCP 服务器
mcp = FastMCP("BigFile MCP Service")

# 工具分类/标签注解（供审计与文档使用）
TOOL_ANNOTATIONS = {
    "file_info": ["meta", "info"],
    "read_bytes": ["io", "read", "bytes"],
    "read_lines": ["io", "read", "lines"],
    "read_last_lines": ["io", "read", "tail"],
    "write_overwrite": ["io", "write", "overwrite"],
    "append": ["io", "write", "append"],
    "insert": ["io", "write", "insert"],
    "build_line_index": ["index", "lines"],
    "line_number_at_offset": ["index", "lines", "query"],
    "search_literal": ["search", "literal"],
    "search_regex": ["search", "regex"],
    "build_inverted_index": ["index", "inverted"],
    "search_index_term": ["index", "query"],
}


@mcp.tool(name="read_bytes")
def tool_read_bytes(file_path: str, offset: int, length: int, encoding: str = settings.default_encoding, ctx: Optional[Any] = None) -> ReadBytesResult:
    """按字节分片读取文件内容。

    参数:
    - file_path: 文件路径
    - offset: 起始字节偏移（>=0）
    - length: 读取长度（>0）
    - encoding: 文本编码
    - ctx: 上下文对象（可选）

    返回:
    - ReadBytesResult: 包含读取到的文本与元信息。
      字段: `data`, `offset`, `bytes_read`, `end_offset`, `file_size`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `offset < 0` 或 `length <= 0` 时抛出。
    """

    logger.info("tool_call", extra={"tool": "read_bytes", "params": {"file_path": file_path, "offset": offset, "length": length, "encoding": encoding}})
    return read_bytes(file_path, offset, length, encoding, max_read_bytes=settings.max_read_bytes)


@mcp.tool(name="read_lines")
def tool_read_lines(file_path: str, start_line: int, num_lines: int, encoding: str = settings.default_encoding, ctx: Optional[Any] = None) -> ReadLinesResult:
    """按行分片读取文件内容。

    参数:
    - file_path: 文件路径
    - start_line: 起始行（>=1）
    - num_lines: 读取行数（>0）
    - encoding: 文本编码
    - ctx: 上下文对象（可选）

    返回:
    - ReadLinesResult: 行读取结果结构。
      字段: `lines`, `start_line`, `end_line`, `total_lines`, `start_offset`, `end_offset`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `start_line < 1` 或 `num_lines <= 0` 时抛出。
    """

    logger.info("tool_call", extra={"tool": "read_lines", "params": {"file_path": file_path, "start_line": start_line, "num_lines": num_lines, "encoding": encoding}})
    return read_lines(file_path, start_line, num_lines, encoding, stream_buffer_bytes=settings.stream_buffer_bytes, index_dir=settings.index_dir)


@mcp.tool(name="read_last_lines")
def tool_read_last_lines(file_path: str, num_lines: int, encoding: str = settings.default_encoding, ctx: Optional[Any] = None) -> ReadLinesResult:
    """读取文件尾部的最后 N 行。

    参数:
    - file_path: 文件路径
    - num_lines: 最后读取的行数（>0）
    - encoding: 文本编码
    - ctx: 上下文对象（可选）

    返回:
    - ReadLinesResult: 与 `tool_read_lines` 返回结构一致。
      字段: `lines`, `start_line`, `end_line`, `total_lines`, `start_offset`, `end_offset`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `num_lines <= 0` 时抛出。
    """

    logger.info("tool_call", extra={"tool": "read_last_lines", "params": {"file_path": file_path, "num_lines": num_lines, "encoding": encoding}})
    return read_last_lines(file_path, num_lines, encoding, stream_buffer_bytes=settings.stream_buffer_bytes, index_dir=settings.index_dir)


@mcp.tool(name="write_overwrite")
def tool_write_overwrite(file_path: str, offset: int, data: str, encoding: str = settings.default_encoding, ctx: Optional[Any] = None) -> WriteResult:
    """覆盖写入：从指定字节偏移开始写入文本数据。

    参数:
    - file_path: 文件路径
    - offset: 写入起始字节偏移
    - data: 文本数据
    - encoding: 文本编码
    - ctx: 上下文对象（可选）

    返回:
    - WriteResult: 写入结果结构。
      字段: `path`, `offset`, `bytes_written`, `end_offset`。

    异常:
    - OSError: 文件写入过程中可能抛出。
    """

    logger.info("tool_call", extra={"tool": "write_overwrite", "params": {"file_path": file_path, "offset": offset, "data_len": len(data), "encoding": encoding}})
    return write_overwrite(file_path, offset, data, encoding, lock_timeout_sec=settings.lock_timeout_sec)


@mcp.tool(name="append")
def tool_append(file_path: str, data: str, encoding: str = settings.default_encoding, ctx: Optional[Any] = None) -> WriteResult:
    """追加写入：在文件末尾追加文本数据。

    参数:
    - file_path: 文件路径
    - data: 文本数据
    - encoding: 文本编码
    - ctx: 上下文对象（可选）

    返回:
    - WriteResult: 写入结果结构。
      字段: `path`, `offset`, `bytes_written`, `end_offset`。

    异常:
    - OSError: 文件写入过程中可能抛出。
    """

    logger.info("tool_call", extra={"tool": "append", "params": {"file_path": file_path, "data_len": len(data), "encoding": encoding}})
    return append_chunk(file_path, data, encoding, lock_timeout_sec=settings.lock_timeout_sec)


@mcp.tool(name="insert")
def tool_insert(file_path: str, offset: int, data: str, encoding: str = settings.default_encoding, temp_dir: Optional[str] = None, ctx: Optional[Any] = None) -> InsertResult:
    """插入写入：在指定字节偏移处插入文本数据（原子替换）。

    参数:
    - file_path: 文件路径
    - offset: 插入偏移
    - data: 文本数据
    - encoding: 文本编码
    - temp_dir: 临时目录（可选）
    - ctx: 上下文对象（可选）

    返回:
    - InsertResult: 插入写入结果结构。
      字段: `path`, `offset`, `bytes_inserted`, `new_size`。

    异常:
    - AssertionError: 当 `offset < 0` 时抛出。
    - OSError: 文件复制/替换过程中可能抛出。
    """

    logger.info("tool_call", extra={"tool": "insert", "params": {"file_path": file_path, "offset": offset, "data_len": len(data), "encoding": encoding, "temp_dir": temp_dir}})
    td = temp_dir
    return insert_chunk(file_path, offset, data, encoding, td, stream_buffer_bytes=settings.stream_buffer_bytes, lock_timeout_sec=settings.lock_timeout_sec)


@mcp.tool(name="file_info")
def tool_file_info(file_path: str, ctx: Optional[Any] = None) -> FileInfo:
    """获取文件基本信息（路径、大小、修改时间）。

    参数:
    - file_path: 文件路径
    - ctx: 上下文对象（可选）

    返回:
    - FileInfo: 文件信息结构。
      字段: `path`, `size`, `mtime`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    """

    logger.info("tool_call", extra={"tool": "file_info", "params": {"file_path": file_path}})
    return get_file_info(file_path)


@mcp.tool(name="build_line_index")
def tool_build_line_index(file_path: str, step: int = 1000, ctx: Optional[Any] = None) -> LineIndexBuildResult:
    """构建行偏移索引（每 step 行记录一次字节偏移）。

    参数:
    - file_path: 目标文件
    - step: 间隔行数
    - ctx: 上下文对象（可选）

    返回:
    - LineIndexBuildResult: 行索引构建结果结构。
      字段: `path`, `index_path`, `entries`, `step`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    """

    logger.info("tool_call", extra={"tool": "build_line_index", "params": {"file_path": file_path, "step": step}})
    return build_line_index(file_path, step=step, encoding=settings.default_encoding, stream_buffer_bytes=settings.stream_buffer_bytes, index_dir=settings.index_dir)


@mcp.tool(name="search_regex")
def tool_search_regex(
    file_path: str,
    pattern: str,
    encoding: str = settings.default_encoding,
    start_offset: int = 0,
    end_offset: Optional[int] = None,
    max_results: int = 200,
    context_chars: int = settings.context_chars,
    flags: Optional[str] = None,
) -> RegexSearchResult:
    """流式正则搜索大文件，返回命中偏移、近似行号及上下文。

    参数:
    - file_path: 文件路径
    - pattern: 正则表达式字符串
    - encoding: 文本编码
    - start_offset: 开始搜索的字节偏移
    - end_offset: 结束搜索的字节偏移（None 表示到文件末尾）
    - max_results: 最大返回条数
    - context_chars: 每个命中项的上下文字符数
    - flags: 正则标志（i,m,s,x），用于控制忽略大小写、多行等

    返回:
    - RegexSearchResult: 正则搜索结果结构。
      `matches` 为列表，元素字段: `start_offset`, `end_offset`, `start_line`, `end_line`, `snippet`；同时包含 `count` 总数。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `start_offset` 与 `end_offset` 区间非法时抛出。
    - re.error: 当正则表达式非法时抛出。
    """
    logger.info("tool_call", extra={"tool": "search_regex", "params": {"file_path": file_path, "pattern": pattern, "start_offset": start_offset, "end_offset": end_offset, "max_results": max_results, "context_chars": context_chars, "flags": flags, "encoding": encoding}})
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


@mcp.tool(name="search_literal")
def tool_search_literal(
    file_path: str,
    query: str,
    encoding: str = settings.default_encoding,
    start_offset: int = 0,
    end_offset: Optional[int] = None,
    max_results: int = 200,
    context_chars: int = settings.context_chars,
    case_sensitive: bool = True,
) -> LiteralSearchResult:
    """流式字面量搜索大文件，返回命中偏移、近似行号及上下文。

    参数:
    - file_path: 文件路径
    - query: 字面量查询字符串
    - encoding: 文本编码
    - start_offset: 开始搜索的字节偏移
    - end_offset: 结束搜索的字节偏移（None 表示到文件末尾）
    - max_results: 最大返回条数
    - context_chars: 每个命中项的上下文字符数
    - case_sensitive: 是否大小写敏感（默认敏感）

    返回:
    - LiteralSearchResult: 字面量搜索结果结构。
      `matches` 为列表，元素字段: `start_offset`, `end_offset`, `start_line`, `end_line`, `snippet`；同时包含 `count` 总数。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `start_offset` 与 `end_offset` 区间非法时抛出。
    """
    logger.info("tool_call", extra={"tool": "search_literal", "params": {"file_path": file_path, "query": query, "start_offset": start_offset, "end_offset": end_offset, "max_results": max_results, "context_chars": context_chars, "case_sensitive": case_sensitive, "encoding": encoding}})
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
logger.info("tools_registered", extra={"count": 13})


@mcp.tool(name="build_inverted_index")
def tool_build_inverted_index(
    file_path: str,
    incremental: bool = True,
    token_pattern: str = r"[\w\-]+",
    lower: bool = True,
) -> BuildInvertedIndexResult:
    """构建或增量更新倒排索引（SQLite 存储）。

    参数:
    - file_path: 目标文件
    - incremental: 是否尝试增量更新（仅支持追加场景）
    - token_pattern: 分词正则表达式（默认匹配字母数字与下划线/连字符）
    - lower: 是否对词项进行小写归一化

    返回:
    - BuildInvertedIndexResult: 倒排索引构建结果结构。
      字段: `db_path`（SQLite 路径）, `mode`（"incremental" 或 "full"）, `indexed_bytes`（本次索引的字节数）。

    说明:
    - 仅支持“末尾追加”的增量更新；若检测到非追加修改将自动触发全量重建。

    异常:
    - FileNotFoundError: 当目标文件不存在或索引文件缺失时抛出。
    """
    logger.info("tool_call", extra={"tool": "build_inverted_index", "params": {"file_path": file_path, "incremental": incremental, "token_pattern": token_pattern, "lower": lower}})
    return build_inverted_index(
        file_path,
        incremental=incremental,
        encoding=settings.default_encoding,
        token_pattern=token_pattern,
        lower=lower,
        stream_buffer_bytes=settings.stream_buffer_bytes,
        index_dir=settings.index_dir,
    )


@mcp.tool(name="search_index_term")
def tool_search_index_term(
    file_path: str,
    term: str,
    prefix: bool = False,
    limit: int = 200,
    context_chars: int = settings.context_chars,
) -> IndexSearchResult:
    """使用倒排索引查询词项，返回命中偏移与上下文片段。

    参数:
    - file_path: 目标文件
    - term: 查询词项（与索引构建的归一化规则一致）
    - prefix: 是否前缀匹配（LIKE term%）
    - limit: 最大返回条数
    - context_chars: 每个命中项的上下文字符数

    返回:
    - IndexSearchResult: 索引查询结果结构。
      `matches` 为列表，元素字段: `term`, `offset`, `end_offset`, `line`, `snippet`；同时包含 `count` 总数。

    异常:
    - FileNotFoundError: 当倒排索引数据库不存在时抛出。
    """
    logger.info("tool_call", extra={"tool": "search_index_term", "params": {"file_path": file_path, "term": term, "prefix": prefix, "limit": limit, "context_chars": context_chars}})
    return search_index_term(
        file_path,
        term,
        prefix=prefix,
        limit=min(limit, settings.max_search_results),
        context_chars=context_chars,
        encoding=settings.default_encoding,
        index_dir=settings.index_dir,
    )


@mcp.tool(name="line_number_at_offset")
def tool_line_number_at_offset(file_path: str, offset: int, ctx: Optional[Any] = None) -> LineNumberResult:
    """根据字节偏移估算行号，若存在索引则快速定位。

    参数:
    - file_path: 文件路径
    - offset: 字节偏移
    - ctx: 上下文对象（可选）

    返回:
    - LineNumberResult: 行号估算结果结构。
      字段: `line`, `scanned_bytes`, `from_checkpoint`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `offset < 0` 时抛出。
    """

    logger.info("tool_call", extra={"tool": "line_number_at_offset", "params": {"file_path": file_path, "offset": offset}})
    return line_number_at_offset(
        file_path,
        offset,
        index_dir=settings.index_dir,
        stream_buffer_bytes=settings.stream_buffer_bytes,
    )