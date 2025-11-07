# API 文档

## 工具列表
- `tool_file_info(path)`
- `tool_read_bytes(path, offset, length, encoding?)`
- `tool_read_lines(path, start_line, num_lines, encoding?)`
- `tool_write_overwrite(path, offset, data, encoding?)`
- `tool_append(path, data, encoding?)`
- `tool_insert(path, offset, data, encoding?, temp_dir?)`
- `tool_build_line_index(path, step?)`
- `tool_line_number_at_offset(path, offset)`
- `tool_search_regex(path, pattern, encoding?, start_offset?, end_offset?, max_results?, context_chars?, flags?)`
- `tool_search_literal(path, query, encoding?, start_offset?, end_offset?, max_results?, context_chars?, case_sensitive?)`
- `tool_build_inverted_index(path, incremental?, token_pattern?, lower?)`
- `tool_search_index_term(path, term, prefix?, limit?, context_chars?)`

## 返回结构约定
- 读取（字节）：`{"data", "offset", "bytes_read", "end_offset", "file_size"}`
- 读取（行）：`{"lines", "start_line", "end_line", "total_lines", "start_offset", "end_offset"}`
- 写入（覆盖/追加）：`{"path", "offset", "bytes_written", "end_offset"}`
- 写入（插入）：`{"path", "offset", "bytes_inserted", "new_size"}`
- 行索引：`{"path", "index_path", "entries", "step"}`
- 偏移到行号：`{"line", "scanned_bytes", "from_checkpoint"}`
- 搜索（通用）：`{"matches": [{...}], "count"}`
- 倒排索引构建：`{"path", "db_path", "mode"}`
- 倒排查询：`{"matches": [{...}], "count"}`

## 错误
- 文件不存在：抛出 `FileNotFoundError`
- 参数非法：断言或抛出相应异常
- 并发写：通过 `locks.py` 保护，超时抛出 `TimeoutError`