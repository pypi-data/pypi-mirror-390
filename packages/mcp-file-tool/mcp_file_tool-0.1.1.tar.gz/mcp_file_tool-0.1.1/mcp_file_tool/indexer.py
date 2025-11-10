import os
import re
import sqlite3
import base64
from typing import Dict, List, Optional, Tuple
from .types import BuildInvertedIndexResult, IndexSearchResult

from .logging_conf import get_logger
from .chunkio import line_number_at_offset, read_bytes

logger = get_logger("indexer")


def _ensure_dir(path: str) -> None:
    """确保目录存在。"""

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)


def _db_path_for(file_path: str, index_dir: str) -> str:
    """得到文件的倒排索引数据库路径。"""

    base = os.path.basename(file_path)
    return os.path.join(index_dir, f"{base}.invidx.sqlite")


def _open_db(db_path: str) -> sqlite3.Connection:
    """打开SQLite数据库并初始化表结构。"""

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS postings (
            term TEXT NOT NULL,
            offset INTEGER NOT NULL,
            end_offset INTEGER NOT NULL,
            line INTEGER,
            PRIMARY KEY (term, offset)
        )
        """
    )
    conn.execute("CREATE INDEX IF NOT EXISTS idx_term ON postings(term);")
    return conn


def _get_meta(conn: sqlite3.Connection, key: str) -> Optional[str]:
    """读取meta键值。"""

    cur = conn.execute("SELECT value FROM meta WHERE key=?", (key,))
    row = cur.fetchone()
    return row[0] if row else None


def _set_meta(conn: sqlite3.Connection, key: str, value: str) -> None:
    """写入meta键值。"""

    conn.execute("INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))


def _tokenize(text: str, regex: re.Pattern, lower: bool) -> List[Tuple[int, int, str]]:
    """对文本进行分词，返回 (start_index, end_index, token)。"""

    tokens: List[Tuple[int, int, str]] = []
    for m in regex.finditer(text):
        tok = m.group(0)
        if lower:
            tok = tok.lower()
        tokens.append((m.start(), m.end(), tok))
    return tokens


def build_inverted_index(
    file_path: str,
    incremental: bool = True,
    encoding: str = "utf-8",
    token_pattern: str = r"[\w\-]+",
    lower: bool = True,
    stream_buffer_bytes: int = 64 * 1024,
    index_dir: str = ".mcp_index",
    tail_bytes_check_len: int = 256,
) -> BuildInvertedIndexResult:
    """构建（或增量更新）倒排索引到SQLite。

    仅对“末尾追加”的场景进行增量更新保证准确性；若检测到非追加修改，将自动触发全量重建。

    参数:
    - file_path: 目标文件
    - incremental: 是否尝试增量更新（仅支持追加）
    - encoding: 文本编码，用于分词与偏移估算
    - token_pattern: 正则表达式，用于分词
    - lower: 是否对token做小写归一
    - stream_buffer_bytes: 流式分块大小
    - index_dir: 索引存储目录
    - tail_bytes_check_len: 追加检测时用于校验的尾部字节快照长度

    返回:
    - BuildInvertedIndexResult: 倒排索引构建结果结构。
      字段: `db_path`（数据库路径）, `mode`（"incremental" 或 "full"）, `indexed_bytes`（本次索引的字节数）。

    异常:
    - FileNotFoundError: 当目标文件不存在时抛出。
    """

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    _ensure_dir(index_dir)
    db_path = _db_path_for(file_path, index_dir)
    conn = _open_db(db_path)
    try:
        st = os.stat(file_path)
        file_size = st.st_size
        file_mtime = int(st.st_mtime)
        prev_indexed_size = int(_get_meta(conn, "indexed_size") or 0)
        prev_mtime = int(_get_meta(conn, "file_mtime") or 0)
        prev_tail_off = int(_get_meta(conn, "tail_snapshot_offset") or 0)
        prev_tail_b64 = _get_meta(conn, "tail_snapshot_bytes")

        # 判断是否可以增量：仅当新size >= 旧size，且尾部校验一致时，视为追加
        can_incremental = False
        if incremental and file_size >= prev_indexed_size and prev_indexed_size > 0:
            # 尾部校验：旧索引末尾处的尾部快照是否与当前文件一致
            check_off = max(prev_indexed_size - tail_bytes_check_len, 0)
            check_len = prev_indexed_size - check_off
            if check_len > 0 and prev_tail_b64:
                cur_tail = read_bytes(file_path, check_off, check_len, encoding=encoding)["data"].encode(encoding)
                old_tail = base64.b64decode(prev_tail_b64)
                if cur_tail == old_tail:
                    can_incremental = True

        # 构造分词正则
        token_re = re.compile(token_pattern)

        def _index_range(start_offset: int, end_offset: int, start_line: int) -> Tuple[int, int]:
            """索引 [start_offset, end_offset) 区间，返回 (indexed_bytes, last_line)。"""

            indexed_bytes = 0
            current_line = start_line
            carry_text = ""
            global_off = start_offset
            # 预编插入语句
            cur = conn.cursor()
            ins = "INSERT INTO postings(term, offset, end_offset, line) VALUES(?,?,?,?) ON CONFLICT(term,offset) DO NOTHING"
            while global_off < end_offset:
                need = min(stream_buffer_bytes, end_offset - global_off)
                b = read_bytes(file_path, global_off, need, encoding=encoding)["data"]
                # b 是字符串，代表这段解码后的文本（可能包含替换字符）
                text = carry_text + b
                tokens = _tokenize(text, token_re, lower)
                # 计算每个token的字节偏移
                for s_idx, e_idx, tok in tokens:
                    # 映射到字节偏移：计算 text[:s_idx] 与 text[:e_idx] 的字节长度
                    s_byte = (text[:s_idx].encode(encoding))
                    e_byte = (text[:e_idx].encode(encoding))
                    start_byte_off = global_off - len(carry_text.encode(encoding)) + len(s_byte)
                    end_byte_off = global_off - len(carry_text.encode(encoding)) + len(e_byte)
                    # 行号估算
                    local_lines = text[:s_idx].count("\n")
                    line_no = current_line + local_lines
                    cur.execute(ins, (tok, start_byte_off, end_byte_off, line_no))
                # 更新carry与行号、偏移
                carry_len = 1024
                carry_text = text[-carry_len:]
                current_line += text.count("\n")
                global_off += len(b.encode(encoding))
                indexed_bytes += len(b.encode(encoding))
            conn.commit()
            return indexed_bytes, current_line

        if can_incremental:
            # 增量：从 prev_indexed_size 到 file_size
            ln_info = line_number_at_offset(file_path, prev_indexed_size, index_dir=index_dir)
            start_line = ln_info.get("line", 1)
            idx_bytes, last_line = _index_range(prev_indexed_size, file_size, start_line)
            mode = "incremental"
            new_indexed_size = file_size
        else:
            # 全量重建
            logger.info("reindex_full", extra={"path": file_path})
            conn.execute("DELETE FROM postings")
            ln_info = line_number_at_offset(file_path, 0, index_dir=index_dir)
            start_line = ln_info.get("line", 1)
            idx_bytes, last_line = _index_range(0, file_size, start_line)
            mode = "full"
            new_indexed_size = file_size

        # 写入meta
        _set_meta(conn, "indexed_size", str(new_indexed_size))
        _set_meta(conn, "file_size", str(file_size))
        _set_meta(conn, "file_mtime", str(file_mtime))
        _set_meta(conn, "encoding", encoding)
        _set_meta(conn, "token_pattern", token_pattern)
        _set_meta(conn, "lower", "1" if lower else "0")
        # 记录尾部快照用于下次增量校验
        tail_off = max(new_indexed_size - tail_bytes_check_len, 0)
        tail_len = new_indexed_size - tail_off
        tail_bytes = read_bytes(file_path, tail_off, tail_len, encoding=encoding)["data"].encode(encoding)
        _set_meta(conn, "tail_snapshot_offset", str(tail_off))
        _set_meta(conn, "tail_snapshot_bytes", base64.b64encode(tail_bytes).decode("ascii"))
        conn.commit()

        logger.info("build_inverted_index_done", extra={"path": file_path, "db": db_path, "mode": mode, "indexed_bytes": idx_bytes})
        return {"db_path": db_path, "mode": mode, "indexed_bytes": idx_bytes}
    finally:
        conn.close()


def search_index_term(
    file_path: str,
    term: str,
    prefix: bool = False,
    limit: int = 200,
    context_chars: int = 96,
    encoding: str = "utf-8",
    index_dir: str = ".mcp_index",
) -> IndexSearchResult:
    """使用倒排索引查询词项，返回命中位置与上下文片段。

    参数:
    - file_path: 目标文件
    - term: 查询词项（已归一化规则与索引一致）
    - prefix: 是否前缀匹配（LIKE term%）
    - limit: 最大返回条数
    - context_chars: 每个命中项的上下文字符数
    - encoding: 文件编码
    - index_dir: 索引目录

    返回:
    - IndexSearchResult: 索引查询结果结构。
      `matches` 为列表，元素字段: `term`, `offset`, `end_offset`, `line`, `snippet`；同时包含 `count` 总数。

    异常:
    - FileNotFoundError: 当倒排索引数据库不存在时抛出。
    """

    db_path = _db_path_for(file_path, index_dir)
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Index not found: {db_path}")

    conn = _open_db(db_path)
    try:
        if prefix:
            q = "SELECT term, offset, end_offset, line FROM postings WHERE term LIKE ? ORDER BY offset LIMIT ?"
            args = (f"{term}%", limit)
        else:
            q = "SELECT term, offset, end_offset, line FROM postings WHERE term = ? ORDER BY offset LIMIT ?"
            args = (term, limit)
        cur = conn.execute(q, args)
        rows = cur.fetchall()
        # 构建片段
        matches: List[Dict] = []
        # 获取文件大小以限制读取范围
        st = os.stat(file_path)
        fsize = st.st_size
        for t, off, end_off, line in rows:
            # 读取上下文（按字节），再解码
            start = max(off - context_chars * 2, 0)
            end = min(end_off + context_chars * 2, fsize)
            chunk = read_bytes(file_path, start, end - start, encoding=encoding)["data"]
            # 在chunk中切片近似片段
            matches.append({
                "term": t,
                "offset": off,
                "end_offset": end_off,
                "line": line,
                "snippet": chunk,
            })
        logger.info("search_index_term", extra={"path": file_path, "term": term, "prefix": prefix, "count": len(matches)})
        return {"matches": matches, "count": len(matches)}
    finally:
        conn.close()