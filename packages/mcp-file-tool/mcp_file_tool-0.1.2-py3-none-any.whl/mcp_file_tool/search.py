import os
import re
from typing import Dict, List, Optional
from .types import RegexSearchResult, LiteralSearchResult

from .logging_conf import get_logger

logger = get_logger("search")


def _validate_file_exists(path: str) -> None:
    """校验文件存在。

    若文件不存在则抛出 FileNotFoundError。
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")


def _resolve_flags(flags: Optional[str]) -> int:
    """将字符串形式的正则标志转换为re模块标志。

    支持字符: i, m, s, x （忽略大小写、多行、点任意、VERBOSE）。
    """

    if not flags:
        return 0
    m = 0
    for ch in flags:
        if ch.lower() == "i":
            m |= re.IGNORECASE
        elif ch.lower() == "m":
            m |= re.MULTILINE
        elif ch.lower() == "s":
            m |= re.DOTALL
        elif ch.lower() == "x":
            m |= re.VERBOSE
    return m


def search_regex(
    file_path: str,
    pattern: str,
    encoding: str = "utf-8",
    start_offset: int = 0,
    end_offset: Optional[int] = None,
    max_results: int = 200,
    context_chars: int = 96,
    stream_buffer_bytes: int = 64 * 1024,
    flags: Optional[str] = None,
) -> RegexSearchResult:
    """在大文件中进行流式正则搜索，返回命中位置与上下文。

    参数:
    - file_path: 文件路径
    - pattern: 正则表达式
    - encoding: 文本编码
    - start_offset: 开始搜索的字节偏移
    - end_offset: 结束搜索的字节偏移（None表示到文件末尾）
    - max_results: 最大返回条数
    - context_chars: 每个命中项前后返回的上下文字符数
    - stream_buffer_bytes: 读取缓冲大小
    - flags: 正则标志字符串（i,m,s,x）

    返回:
    - RegexSearchResult: 正则搜索结果结构。
      `matches` 为列表，元素字段: `start_offset`, `end_offset`, `start_line`, `end_line`, `snippet`；同时包含 `count` 总数。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `start_offset` 与 `end_offset` 区间非法时抛出。
    - re.error: 当正则表达式非法时抛出。
    """

    _validate_file_exists(file_path)
    st = os.stat(file_path)
    if end_offset is None:
        end_offset = st.st_size
    assert start_offset >= 0 and start_offset <= end_offset, "offset 区间非法"

    regex = re.compile(pattern, _resolve_flags(flags))

    matches: List[Dict] = []
    global_offset = start_offset
    carry = b""  # 跨块匹配的余量
    line_no = 1

    # 计算起始行号（流式到start_offset）
    with open(file_path, "rb") as f:
        to_seek = start_offset
        while to_seek > 0:
            chunk = f.read(min(stream_buffer_bytes, to_seek))
            if not chunk:
                break
            line_no += chunk.count(b"\n")
            to_seek -= len(chunk)

    with open(file_path, "rb") as f:
        f.seek(start_offset)
        while global_offset < end_offset:
            need = min(stream_buffer_bytes, end_offset - global_offset)
            b = f.read(need)
            if not b:
                break

            data = carry + b
            text = data.decode(encoding, errors="replace")

            # 查找命中，定位偏移与行号增量
            for m in regex.finditer(text):
                if len(matches) >= max_results:
                    break
                m_start_rel = m.start()
                m_end_rel = m.end()
                m_start = global_offset - len(carry) + len(text[:m_start_rel].encode(encoding, errors="replace"))
                m_end = global_offset - len(carry) + len(text[:m_end_rel].encode(encoding, errors="replace"))

                # 基于当前块估计行号（近似，足以定位）
                # 为精确行号，可在未来基于line索引优化。
                within = text[:m_start_rel]
                local_lines = within.count("\n")
                start_line = line_no + local_lines
                end_line = start_line + text[m_start_rel:m_end_rel].count("\n")

                # 片段上下文
                s_start = max(m_start_rel - context_chars, 0)
                s_end = min(m_end_rel + context_chars, len(text))
                snippet = text[s_start:s_end]
                matches.append({
                    "start_offset": m_start,
                    "end_offset": m_end,
                    "start_line": start_line,
                    "end_line": end_line,
                    "snippet": snippet,
                })

            if len(matches) >= max_results:
                break

            # 更新携带余量以覆盖跨块边界（最多保留pattern长度的两倍字符）
            # 若无法确定pattern长度，保留 context_chars 的两倍作为安全余量。
            carry_text_len = max(context_chars * 2, 256)
            carry = text[-carry_text_len:].encode(encoding, errors="replace")

            # 行号推进
            line_no += text.count("\n")
            global_offset += len(b)

    logger.info("search_regex", extra={"path": file_path, "pattern": pattern, "matches": len(matches)})
    return {"matches": matches, "count": len(matches)}


def search_literal(
    file_path: str,
    query: str,
    encoding: str = "utf-8",
    start_offset: int = 0,
    end_offset: Optional[int] = None,
    max_results: int = 200,
    context_chars: int = 96,
    stream_buffer_bytes: int = 64 * 1024,
    case_sensitive: bool = True,
) -> LiteralSearchResult:
    """在大文件中进行流式字面量搜索。

    参数:
    - file_path: 文件路径
    - query: 字面量查询字符串
    - encoding: 文本编码
    - start_offset: 开始偏移
    - end_offset: 结束偏移
    - max_results: 最大条数
    - context_chars: 上下文长度
    - stream_buffer_bytes: 缓冲大小
    - case_sensitive: 是否大小写敏感

    返回:
    - LiteralSearchResult: 字面量搜索结果结构。
      `matches` 为列表，元素字段: `start_offset`, `end_offset`, `start_line`, `end_line`, `snippet`；同时包含 `count` 总数。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `start_offset` 与 `end_offset` 区间非法时抛出。
    """

    _validate_file_exists(file_path)
    st = os.stat(file_path)
    if end_offset is None:
        end_offset = st.st_size
    assert start_offset >= 0 and start_offset <= end_offset, "offset 区间非法"

    q = query if case_sensitive else query.lower()

    matches: List[Dict] = []
    global_offset = start_offset
    carry = ""
    line_no = 1

    # 起始行估计
    with open(file_path, "rb") as f:
        to_seek = start_offset
        while to_seek > 0:
            chunk = f.read(min(stream_buffer_bytes, to_seek))
            if not chunk:
                break
            line_no += chunk.count(b"\n")
            to_seek -= len(chunk)

    with open(file_path, "rb") as f:
        f.seek(start_offset)
        while global_offset < end_offset:
            need = min(stream_buffer_bytes, end_offset - global_offset)
            b = f.read(need)
            if not b:
                break
            text = carry + b.decode(encoding, errors="replace")
            target = text if case_sensitive else text.lower()
            pos = 0
            while len(matches) < max_results:
                idx = target.find(q, pos)
                if idx == -1:
                    break
                m_start = global_offset - len(carry.encode(encoding)) + len(text[:idx].encode(encoding))
                m_end = m_start + len(q.encode(encoding))
                local_lines = text[:idx].count("\n")
                start_line = line_no + local_lines
                end_line = start_line + text[idx:idx + len(q)].count("\n")
                s_start = max(idx - context_chars, 0)
                s_end = min(idx + len(q) + context_chars, len(text))
                snippet = text[s_start:s_end]
                matches.append({
                    "start_offset": m_start,
                    "end_offset": m_end,
                    "start_line": start_line,
                    "end_line": end_line,
                    "snippet": snippet,
                })
                pos = idx + len(q)

            if len(matches) >= max_results:
                break

            carry_len = max(context_chars * 2, len(q) * 2, 256)
            carry = text[-carry_len:]
            line_no += text.count("\n")
            global_offset += len(b)

    logger.info("search_literal", extra={"path": file_path, "query": query, "matches": len(matches)})
    return {"matches": matches, "count": len(matches)}