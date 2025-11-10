import io
import os
import time
from typing import Dict, List, Optional, Tuple
from .types import (
    FileInfo,
    ReadBytesResult,
    ReadLinesResult,
    WriteResult,
    InsertResult,
    LineIndexBuildResult,
    LineNumberResult,
)

from .logging_conf import get_logger
from .locks import file_lock

logger = get_logger("chunkio")


def _validate_file_exists(path: str) -> None:
    """校验文件存在。

    若文件不存在则抛出 FileNotFoundError。
    """

    if not os.path.isfile(path):
        raise FileNotFoundError(f"File not found: {path}")


def _clamp(value: int, min_v: int, max_v: Optional[int]) -> int:
    """约束数值到指定区间。

    - value: 输入值
    - min_v: 最小值
    - max_v: 最大值（可选）
    返回约束后的值。
    """

    if value < min_v:
        return min_v
    if max_v is not None and value > max_v:
        return max_v
    return value


def get_file_info(file_path: str) -> FileInfo:
    """获取文件基本信息（路径、大小、修改时间，秒级）。

    参数:
    - file_path: 文件路径。

    返回:
    - FileInfo: 文件信息结构，字段: `path`, `size`, `mtime`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    """

    _validate_file_exists(file_path)
    st = os.stat(file_path)
    info = {
        "path": file_path,
        "size": st.st_size,
        "mtime": int(st.st_mtime),
    }
    logger.info("file_info", extra={"info": info})
    return info


def read_bytes(
    file_path: str,
    offset: int,
    length: int,
    encoding: str = "utf-8",
    max_read_bytes: Optional[int] = None,
) -> ReadBytesResult:
    """按字节分片读取文件，适合大文件范围读取。

    参数:
    - file_path: 文件路径
    - offset: 起始字节偏移（>=0）
    - length: 读取字节长度（>0）
    - encoding: 文本编码（用于解码返回）
    - max_read_bytes: 单次读取最大上限（用于保护上下文）

    返回:
    - ReadBytesResult: 读取（字节）结果结构。
      字段: `data`, `offset`, `bytes_read`, `end_offset`, `file_size`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `offset` < 0 或 `length` <= 0 时抛出。
    """

    _validate_file_exists(file_path)
    assert offset >= 0, "offset 必须>=0"
    assert length > 0, "length 必须>0"

    st = os.stat(file_path)
    file_size = st.st_size
    end = min(offset + length, file_size)
    if max_read_bytes is not None:
        end = min(end, offset + max_read_bytes)

    with open(file_path, "rb") as f:
        f.seek(offset)
        raw = f.read(end - offset)
    data = raw.decode(encoding, errors="replace")
    res = {
        "data": data,
        "offset": offset,
        "bytes_read": len(raw),
        "end_offset": offset + len(raw),
        "file_size": file_size,
    }
    logger.info("read_bytes", extra={"path": file_path, "offset": offset, "length": length, "result": {k: v for k, v in res.items() if k != "data"}})
    return res


def read_lines(
    file_path: str,
    start_line: int,
    num_lines: int,
    encoding: str = "utf-8",
    stream_buffer_bytes: int = 64 * 1024,
    index_dir: Optional[str] = None,
) -> ReadLinesResult:
    """按行分片读取文件（支持行索引加速）。

    优化：若提供并存在 `<base>.lineidx.json` 行索引，将使用最近的行标记快速定位到
    `start_line` 的近似字节偏移，避免从文件头全量扫描，大幅提升随机行访问性能。

    参数:
    - file_path: 文件路径
    - start_line: 起始行（>=1）
    - num_lines: 读取行数（>0）
    - encoding: 文本编码
    - stream_buffer_bytes: 流式行扫描的缓冲大小
    - index_dir: 行索引目录（可选）

    返回:
    - ReadLinesResult: 读取（行）结果结构。
      字段: `lines`, `start_line`, `end_line`, `total_lines`, `start_offset`, `end_offset`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `start_line` < 1 或 `num_lines` <= 0 时抛出。
    """

    _validate_file_exists(file_path)
    assert start_line >= 1, "start_line 必须>=1"
    assert num_lines > 0, "num_lines 必须>0"

    # 先尝试使用索引定位起始偏移
    current_line = 1
    start_offset = 0
    used_index = False
    if index_dir is not None:
        base = os.path.basename(file_path)
        idx_path = os.path.join(index_dir, f"{base}.lineidx.json")
        if os.path.exists(idx_path):
            try:
                import json
                with open(idx_path, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                entries = obj.get("entries", [])
                checkpoint_line = 1
                checkpoint_offset = 0
                for ln, boff in entries:
                    if ln <= start_line and ln >= checkpoint_line:
                        checkpoint_line = ln
                        checkpoint_offset = boff
                current_line = checkpoint_line
                start_offset = checkpoint_offset
                used_index = True
            except Exception:
                used_index = False

    # 从已定位偏移继续推进到目标起始行
    with open(file_path, "rb") as f:
        f.seek(start_offset)
        buf = b""
        while current_line < start_line:
            chunk = f.read(stream_buffer_bytes)
            if not chunk:
                break
            buf += chunk
            while True:
                idx = buf.find(b"\n")
                if idx == -1:
                    break
                start_offset += idx + 1
                current_line += 1
                buf = buf[idx + 1 :]
                if current_line >= start_line:
                    break
            if current_line >= start_line:
                break
        # 若未达到目标行但文件结束，返回空
        if current_line < start_line:
            return {
                "lines": [],
                "start_line": start_line,
                "end_line": start_line - 1,
                "total_lines": current_line - 1,
                "start_offset": start_offset,
                "end_offset": start_offset,
            }

    # 从起始偏移按行读取 num_lines
    lines: List[str] = []
    end_offset = start_offset
    with open(file_path, "rb") as f:
        f.seek(start_offset)
        for _ in range(num_lines):
            line = f.readline()
            if not line:
                break
            lines.append(line.decode(encoding, errors="replace"))
            end_offset += len(line)

    end_line = start_line + len(lines) - 1
    # 统计总行数：优先使用索引尾标记 + 尾部扫描；无索引则回退全文件扫描
    total_lines = 0
    used_index_tail = False
    if index_dir is not None:
        base = os.path.basename(file_path)
        idx_path = os.path.join(index_dir, f"{base}.lineidx.json")
        if os.path.exists(idx_path):
            try:
                import json
                with open(idx_path, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                entries = obj.get("entries", [])
                tail_checkpoint_line = 1
                tail_checkpoint_offset = 0
                for ln, boff in entries:
                    if ln >= tail_checkpoint_line:
                        tail_checkpoint_line = ln
                        tail_checkpoint_offset = boff
                tail_lines = 0
                with open(file_path, "rb") as f:
                    f.seek(tail_checkpoint_offset)
                    while True:
                        chunk = f.read(stream_buffer_bytes)
                        if not chunk:
                            break
                        tail_lines += chunk.count(b"\n")
                total_lines = tail_checkpoint_line + tail_lines
                # 若最后一字节不是换行，补计一行
                st = os.stat(file_path)
                if st.st_size > 0:
                    with open(file_path, "rb") as f:
                        f.seek(st.st_size - 1)
                        if f.read(1) != b"\n":
                            total_lines += 1
                used_index_tail = True
            except Exception:
                used_index_tail = False
    if not used_index_tail:
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(stream_buffer_bytes)
                if not chunk:
                    break
                total_lines += chunk.count(b"\n")
        # 若最后一行未以\n结束，仍算作一行
        try:
            st = os.stat(file_path)
            if st.st_size > 0:
                with open(file_path, "rb") as f:
                    f.seek(st.st_size - 1)
                    if f.read(1) != b"\n":
                        total_lines += 1
        except Exception:
            pass

    res = {
        "lines": lines,
        "start_line": start_line,
        "end_line": end_line,
        "total_lines": total_lines,
        "start_offset": start_offset,
        "end_offset": end_offset,
    }
    logger.info("read_lines", extra={"path": file_path, "start_line": start_line, "num_lines": num_lines, "result": {k: v for k, v in res.items() if k != "lines"}})
    return res


def read_last_lines(
    file_path: str,
    num_lines: int,
    encoding: str = "utf-8",
    stream_buffer_bytes: int = 64 * 1024,
    index_dir: Optional[str] = None,
) -> ReadLinesResult:
    """读取文件的最后 N 行（尾部查看优化）。

    自末尾向前分块扫描，定位最后 N 行的起始偏移；若存在行索引，
    将通过尾部检查点快速估算总行数，以给出准确的起止行号。

    返回:
    - ReadLinesResult: 读取（行）结果结构，与 `read_lines` 一致。
      字段: `lines`, `start_line`, `end_line`, `total_lines`, `start_offset`, `end_offset`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `num_lines` <= 0 时抛出。
    """

    _validate_file_exists(file_path)
    assert num_lines > 0, "num_lines 必须>0"

    st = os.stat(file_path)
    file_size = st.st_size

    needed_newlines = num_lines
    pos = file_size
    buf_parts: List[bytes] = []
    newlines_found = 0
    with open(file_path, "rb") as f:
        while pos > 0 and newlines_found < needed_newlines:
            read_len = min(stream_buffer_bytes, pos)
            pos -= read_len
            f.seek(pos)
            chunk = f.read(read_len)
            buf_parts.insert(0, chunk)
            newlines_found += chunk.count(b"\n")

    full_buf = b"".join(buf_parts)
    start_rel = 0
    if newlines_found >= needed_newlines:
        cnt = 0
        for i in range(len(full_buf) - 1, -1, -1):
            if full_buf[i:i+1] == b"\n":
                cnt += 1
                if cnt == needed_newlines:
                    start_rel = i + 1
                    break

    start_offset = file_size - len(full_buf) + start_rel
    end_offset = file_size

    text = full_buf.decode(encoding, errors="replace")
    lines_all = text.split("\n")
    lines = lines_all[-num_lines:] if len(lines_all) >= num_lines else lines_all

    total_lines = 0
    used_index_tail = False
    if index_dir is not None:
        base = os.path.basename(file_path)
        idx_path = os.path.join(index_dir, f"{base}.lineidx.json")
        if os.path.exists(idx_path):
            try:
                import json
                with open(idx_path, "r", encoding="utf-8") as f:
                    obj = json.load(f)
                entries = obj.get("entries", [])
                tail_checkpoint_line = 1
                tail_checkpoint_offset = 0
                for ln, boff in entries:
                    if ln >= tail_checkpoint_line:
                        tail_checkpoint_line = ln
                        tail_checkpoint_offset = boff
                tail_lines = 0
                with open(file_path, "rb") as f:
                    f.seek(tail_checkpoint_offset)
                    while True:
                        c = f.read(stream_buffer_bytes)
                        if not c:
                            break
                        tail_lines += c.count(b"\n")
                total_lines = tail_checkpoint_line + tail_lines
                # 最后一字节不是换行时，补计一行
                if file_size > 0:
                    with open(file_path, "rb") as f:
                        f.seek(file_size - 1)
                        if f.read(1) != b"\n":
                            total_lines += 1
                used_index_tail = True
            except Exception:
                used_index_tail = False
    if not used_index_tail:
        with open(file_path, "rb") as f:
            while True:
                c = f.read(stream_buffer_bytes)
                if not c:
                    break
                total_lines += c.count(b"\n")
        # 最后一字节不是换行时，补计一行
        if file_size > 0:
            with open(file_path, "rb") as f:
                f.seek(file_size - 1)
                if f.read(1) != b"\n":
                    total_lines += 1

    end_line = total_lines
    start_line = max(end_line - len(lines) + 1, 1)

    res = {
        "lines": lines,
        "start_line": start_line,
        "end_line": end_line,
        "total_lines": total_lines,
        "start_offset": start_offset,
        "end_offset": end_offset,
    }
    logger.info("read_last_lines", extra={"path": file_path, "num_lines": num_lines, "result": {k: v for k, v in res.items() if k != "lines"}})
    return res


def write_overwrite(
    file_path: str,
    offset: int,
    data: str,
    encoding: str = "utf-8",
    lock_timeout_sec: int = 10,
) -> WriteResult:
    """按字节偏移覆盖写入，不改变其他字节。

    参数:
    - file_path: 文件路径（不存在则创建空文件再写入）
    - offset: 写入起始字节偏移
    - data: 待写入文本数据
    - encoding: 文本编码

    返回:
    - WriteResult: 写入（覆盖）结果结构。
      字段: `path`, `offset`, `bytes_written`, `end_offset`。

    并发:
    - 使用文件锁保护并发写入，锁超时将抛出 `TimeoutError`。
    """

    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    raw = data.encode(encoding)
    with file_lock(file_path, timeout_sec=lock_timeout_sec):
        mode = "r+b" if os.path.exists(file_path) else "wb"
        with open(file_path, mode) as f:
            f.seek(offset)
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
            end_offset = f.tell()
    res = {
        "path": file_path,
        "offset": offset,
        "bytes_written": len(raw),
        "end_offset": end_offset,
    }
    logger.info("write_overwrite", extra={"path": file_path, "offset": offset, "bytes_written": len(raw)})
    return res


def append_chunk(file_path: str, data: str, encoding: str = "utf-8", lock_timeout_sec: int = 10) -> WriteResult:
    """在文件末尾追加文本数据。

    参数:
    - file_path: 文件路径
    - data: 文本数据
    - encoding: 文本编码

    返回:
    - WriteResult: 写入（追加）结果结构。
      字段: `path`, `offset`, `bytes_written`, `end_offset`。

    并发:
    - 使用文件锁保护并发写入，锁超时将抛出 `TimeoutError`。
    """

    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    raw = data.encode(encoding)
    with file_lock(file_path, timeout_sec=lock_timeout_sec):
        with open(file_path, "ab") as f:
            f.seek(0, io.SEEK_END)
            offset = f.tell()
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
            end_offset = f.tell()
    res = {
        "path": file_path,
        "offset": offset,
        "bytes_written": len(raw),
        "end_offset": end_offset,
    }
    logger.info("append_chunk", extra={"path": file_path, "offset": offset, "bytes_written": len(raw)})
    return res


def insert_chunk(
    file_path: str,
    offset: int,
    data: str,
    encoding: str = "utf-8",
    temp_dir: Optional[str] = None,
    stream_buffer_bytes: int = 64 * 1024,
    lock_timeout_sec: int = 10,
) -> InsertResult:
    """在指定字节偏移处插入文本数据（安全、流式、原子替换）。

    实现：以流式复制原文件到临时文件，在offset处写入新增数据，再复制剩余部分，最终原子替换。

    参数:
    - file_path: 目标文件
    - offset: 插入偏移（>=0）
    - data: 文本数据
    - encoding: 编码
    - temp_dir: 临时目录（默认系统临时目录）
    - stream_buffer_bytes: 流式复制缓冲大小

    返回:
    - InsertResult: 写入（插入）结果结构。
      字段: `path`, `offset`, `bytes_inserted`, `new_size`。

    异常:
    - AssertionError: 当 `offset` < 0 时抛出。
    - TimeoutError: 文件锁获取超时。
    """

    assert offset >= 0, "offset 必须>=0"
    os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)
    raw = data.encode(encoding)

    # 若文件不存在，直接创建并写入
    if not os.path.exists(file_path):
        with open(file_path, "wb") as nf:
            nf.write(raw)
            nf.flush()
            os.fsync(nf.fileno())
        st = os.stat(file_path)
        logger.info("insert_chunk_create", extra={"path": file_path, "bytes_inserted": len(raw)})
        return {"path": file_path, "offset": 0, "bytes_inserted": len(raw), "new_size": st.st_size}

    base = os.path.basename(file_path)
    tmp_dir = temp_dir or os.path.dirname(file_path) or "."
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f".{base}.tmp.{int(time.time())}")

    with file_lock(file_path, timeout_sec=lock_timeout_sec):
        with open(file_path, "rb") as src, open(tmp_path, "wb") as dst:
            # 复制前半段
            to_copy = offset
            while to_copy > 0:
                chunk = src.read(min(stream_buffer_bytes, to_copy))
                if not chunk:
                    break
                dst.write(chunk)
                to_copy -= len(chunk)
            # 写入插入内容
            dst.write(raw)
            # 复制后半段
            while True:
                chunk = src.read(stream_buffer_bytes)
                if not chunk:
                    break
                dst.write(chunk)
            dst.flush()
            os.fsync(dst.fileno())

    # 原子替换
    os.replace(tmp_path, file_path)
    st = os.stat(file_path)
    res = {"path": file_path, "offset": offset, "bytes_inserted": len(raw), "new_size": st.st_size}
    logger.info("insert_chunk", extra=res)
    return res


def build_line_index(
    file_path: str,
    step: int = 1000,
    encoding: str = "utf-8",
    stream_buffer_bytes: int = 64 * 1024,
    index_dir: str = ".mcp_index",
) -> LineIndexBuildResult:
    """为大文件构建行偏移索引（每 step 行记录一次字节偏移）。

    索引文件输出到 index_dir 下，文件名形如 `<base>.lineidx.json`。

    参数:
    - file_path: 目标文件
    - step: 间隔行数
    - encoding: 编码（仅用于日志显示，不影响计算）
    - stream_buffer_bytes: 缓冲大小
    - index_dir: 索引目录

    返回:
    - LineIndexBuildResult: 行索引构建结果结构。
      字段: `path`, `index_path`, `entries`, `step`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    """

    _validate_file_exists(file_path)
    os.makedirs(index_dir, exist_ok=True)
    base = os.path.basename(file_path)
    idx_path = os.path.join(index_dir, f"{base}.lineidx.json")

    entries: List[Tuple[int, int]] = []  # (line_no, byte_offset)
    line_no = 1
    byte_offset = 0
    next_mark = step
    with open(file_path, "rb") as f:
        buf = b""
        while True:
            chunk = f.read(stream_buffer_bytes)
            if not chunk:
                break
            buf += chunk
            while True:
                idx = buf.find(b"\n")
                if idx == -1:
                    break
                byte_offset += idx + 1
                if line_no == next_mark:
                    entries.append((line_no, byte_offset))
                    next_mark += step
                line_no += 1
                buf = buf[idx + 1 :]
        # 文件末尾无\n仍算一行，但不记录偏移标记

    # 写出索引文件
    import json

    obj = {"path": file_path, "step": step, "entries": entries}
    with open(idx_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    logger.info("build_line_index", extra={"path": file_path, "index_path": idx_path, "entries": len(entries), "step": step})
    return {"path": file_path, "index_path": idx_path, "entries": len(entries), "step": step}


def line_number_at_offset(
    file_path: str,
    offset: int,
    index_dir: str = ".mcp_index",
    stream_buffer_bytes: int = 64 * 1024,
) -> LineNumberResult:
    """根据偏移估算行号，优先使用索引文件加速。

    若存在 `<base>.lineidx.json` 索引，将从最近的标记偏移处开始扫描到目标偏移。
    否则，从文件头开始扫描。

    参数:
    - file_path: 目标文件
    - offset: 目标字节偏移
    - index_dir: 索引目录
    - stream_buffer_bytes: 缓冲大小

    返回:
    - LineNumberResult: 偏移估算行号结果结构。
      字段: `line`, `scanned_bytes`, `from_checkpoint`。

    异常:
    - FileNotFoundError: 当文件不存在时抛出。
    - AssertionError: 当 `offset` < 0 时抛出。
    """

    _validate_file_exists(file_path)
    assert offset >= 0, "offset 必须>=0"

    import json

    base = os.path.basename(file_path)
    idx_path = os.path.join(index_dir, f"{base}.lineidx.json")
    checkpoint_offset = 0
    checkpoint_line = 1
    used_checkpoint = False
    if os.path.exists(idx_path):
        try:
            with open(idx_path, "r", encoding="utf-8") as f:
                obj = json.load(f)
            entries = obj.get("entries", [])
            # 找到不超过offset的最大偏移标记
            for ln, boff in entries:
                if boff <= offset and boff >= checkpoint_offset:
                    checkpoint_offset = boff
                    checkpoint_line = ln
                    used_checkpoint = True
        except Exception:
            used_checkpoint = False

    scanned = 0
    with open(file_path, "rb") as f:
        f.seek(checkpoint_offset)
        remaining = offset - checkpoint_offset
        while remaining > 0:
            chunk = f.read(min(stream_buffer_bytes, remaining))
            if not chunk:
                break
            cnt = chunk.count(b"\n")
            checkpoint_line += cnt
            scanned += len(chunk)
            remaining -= len(chunk)

    logger.info("line_number_at_offset", extra={"path": file_path, "offset": offset, "line": checkpoint_line, "used_checkpoint": used_checkpoint})
    return {"line": checkpoint_line, "scanned_bytes": scanned, "from_checkpoint": used_checkpoint}