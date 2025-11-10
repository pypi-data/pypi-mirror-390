# API 文档

## 工具列表（导出名）
- `file_info(file_path)`
- `read_bytes(file_path, offset, length, encoding?)`
- `read_lines(file_path, start_line, num_lines, encoding?)`
- `read_last_lines(file_path, num_lines, encoding?)`
- `write_overwrite(file_path, offset, data, encoding?)`
- `append(file_path, data, encoding?)`
- `insert(file_path, offset, data, encoding?, temp_dir?)`
- `build_line_index(file_path, step?)`
- `line_number_at_offset(file_path, offset)`
- `search_regex(file_path, pattern, encoding?, start_offset?, end_offset?, max_results?, context_chars?, flags?)`
- `search_literal(file_path, query, encoding?, start_offset?, end_offset?, max_results?, context_chars?, case_sensitive?)`
- `build_inverted_index(file_path, incremental?, token_pattern?, lower?)`
- `search_index_term(file_path, term, prefix?, limit?, context_chars?)`

## 通用约定
- 所有工具支持可选参数 `ctx`（上下文对象），用于日志追踪与审计，不影响功能逻辑。为简洁起见，上述签名中省略了 `ctx`。
- 返回结构采用 `TypedDict` 类型定义，位于 `mcp_file_tool/types.py`，便于解析与静态检查。
  - `file_info` → `FileInfo`
  - `read_bytes` → `ReadBytesResult`
  - `read_lines`/`read_last_lines` → `ReadLinesResult`
  - `write_overwrite`/`append` → `WriteResult`
  - `insert` → `InsertResult`
  - `build_line_index` → `LineIndexBuildResult`
  - `line_number_at_offset` → `LineNumberResult`
  - `search_regex` → `RegexSearchResult`
  - `search_literal` → `LiteralSearchResult`
  - `build_inverted_index` → `BuildInvertedIndexResult`
  - `search_index_term` → `IndexSearchResult`

## 工具说明

### file_info(file_path)
- 说明：获取文件基本信息（路径、大小、修改时间，秒级）。
- 参数：
  - `file_path` 文件路径。
- 返回：`{"path","size","mtime"}`。
 - 返回类型：`FileInfo`

### read_bytes(file_path, offset, length, encoding?)
- 说明：按字节分片读取文件内容，适合大文件范围读取。
- 参数：
  - `file_path` 目标文件路径。
  - `offset` 起始字节偏移（>=0）。
  - `length` 读取长度（>0）。
  - `encoding` 文本编码，默认使用服务端配置。
- 返回：`{"data","offset","bytes_read","end_offset","file_size"}`。
- 备注：单次读取受服务端 `max_read_bytes` 上限保护。
 - 返回类型：`ReadBytesResult`

### read_lines(file_path, start_line, num_lines, encoding?)
- 说明：按行分片读取文件内容；如存在行索引则加速定位起始偏移，否则采用流式扫描。
- 参数：
  - `file_path` 目标文件路径。
  - `start_line` 起始行（>=1）。
  - `num_lines` 读取行数（>0）。
  - `encoding` 文本编码。
- 返回：`{"lines","start_line","end_line","total_lines","start_offset","end_offset"}`。
 - 返回类型：`ReadLinesResult`

### read_last_lines(file_path, num_lines, encoding?)
- 说明：高效读取文件尾部的最后 N 行；如存在行索引则从靠近文件尾的检查点回扫，否则自尾部流式回扫。
- 参数：
  - `file_path` 目标文件路径。
  - `num_lines` 最后读取的行数（>0）。
  - `encoding` 文本编码。
- 返回：与 `read_lines` 一致：`{"lines","start_line","end_line","total_lines","start_offset","end_offset"}`。
 - 返回类型：`ReadLinesResult`

### write_overwrite(file_path, offset, data, encoding?)
- 说明：按字节偏移覆盖写入，不改变其他字节。
- 参数：
  - `file_path` 目标文件（不存在则创建）。
  - `offset` 写入起始字节偏移。
  - `data` 文本数据。
  - `encoding` 文本编码。
- 返回：`{"path","offset","bytes_written","end_offset"}`。
- 并发：受文件锁保护，超时抛出 `TimeoutError`。
 - 返回类型：`WriteResult`

### append(file_path, data, encoding?)
- 说明：在文件末尾追加文本数据。
- 参数：
  - `file_path` 目标文件。
  - `data` 文本数据。
  - `encoding` 文本编码。
- 返回：`{"path","offset","bytes_written","end_offset"}`。
 - 返回类型：`WriteResult`

### insert(file_path, offset, data, encoding?, temp_dir?)
- 说明：在指定字节偏移处插入文本（流式复制，原子替换）。
- 参数：
  - `file_path` 目标文件。
  - `offset` 插入偏移（>=0）。
  - `data` 文本数据。
  - `encoding` 文本编码。
  - `temp_dir` 临时目录（可选）。
- 返回：`{"path","offset","bytes_inserted","new_size"}`。
 - 返回类型：`InsertResult`

### build_line_index(file_path, step?)
- 说明：为大文件构建行偏移索引（每 `step` 行记录一次字节偏移）。
- 参数：
  - `file_path` 目标文件。
  - `step` 间隔行数（默认 1000）。
- 返回：`{"path","index_path","entries","step"}`。
- 索引位置：默认写入 `settings.index_dir` 下，文件名 `<base>.lineidx.json`。
 - 返回类型：`LineIndexBuildResult`

### line_number_at_offset(file_path, offset)
- 说明：根据字节偏移估算行号，优先利用行索引文件加速。
- 参数：
  - `file_path` 目标文件。
  - `offset` 目标字节偏移。
- 返回：`{"line","scanned_bytes","from_checkpoint"}`。
 - 返回类型：`LineNumberResult`

### search_regex(file_path, pattern, encoding?, start_offset?, end_offset?, max_results?, context_chars?, flags?)
- 说明：流式正则搜索大文件，返回命中偏移、近似行号及上下文片段。
- 参数：
  - `file_path` 目标文件。
  - `pattern` 正则表达式。
  - `encoding` 文本编码。
  - `start_offset` 起始偏移（字节）。
  - `end_offset` 结束偏移（字节，默认到文件尾）。
  - `max_results` 最大返回条数（受服务端上限约束）。
  - `context_chars` 每个命中项前后返回的上下文字符数。
  - `flags` 正则标志字符串，支持 `i`、`m`、`s`、`x`。
- 返回：`{"matches":[{"start_offset","end_offset","start_line","end_line","snippet"}],"count"}`。
 - 返回类型：`RegexSearchResult`

### search_literal(file_path, query, encoding?, start_offset?, end_offset?, max_results?, context_chars?, case_sensitive?)
- 说明：流式字面量搜索大文件。
- 参数：
  - `file_path` 目标文件。
  - `query` 字面量查询字符串。
  - `encoding` 文本编码。
  - `start_offset` 起始偏移（字节）。
  - `end_offset` 结束偏移（字节，默认到文件尾）。
  - `max_results` 最大返回条数（受服务端上限约束）。
  - `context_chars` 每个命中项前后返回的上下文字符数。
  - `case_sensitive` 是否大小写敏感。
- 返回：`{"matches":[{"start_offset","end_offset","start_line","end_line","snippet"}],"count"}`。
 - 返回类型：`LiteralSearchResult`

### build_inverted_index(file_path, incremental?, token_pattern?, lower?)
- 说明：构建或增量更新倒排索引（SQLite 存储）。
- 参数：
  - `file_path` 目标文件。
  - `incremental` 是否尝试增量（仅支持末尾追加）。
  - `token_pattern` 分词正则。
  - `lower` 是否小写归一。
- 返回：`{"db_path","mode","indexed_bytes"}`。
- 索引位置：默认写入 `settings.index_dir`，路径形如 `~/.mft/.mcp_index/<base>.invidx.sqlite`。
 - 返回类型：`BuildInvertedIndexResult`

### search_index_term(file_path, term, prefix?, limit?, context_chars?)
- 说明：使用倒排索引查询词项，返回命中位置与上下文片段。
- 参数：
  - `file_path` 目标文件。
  - `term` 查询词项（与索引归一规则一致）。
  - `prefix` 前缀匹配。
  - `limit` 最大返回条数（受服务端上限约束）。
  - `context_chars` 上下文字符数。
- 返回：`{"matches":[{"term","offset","end_offset","line","snippet"}],"count"}`。
 - 返回类型：`IndexSearchResult`

## 返回结构约定
- 文件信息：`{"path","size","mtime"}`
- 读取（字节）：`{"data","offset","bytes_read","end_offset","file_size"}`
- 读取（行）：`{"lines","start_line","end_line","total_lines","start_offset","end_offset"}`
- 写入（覆盖/追加）：`{"path","offset","bytes_written","end_offset"}`
- 写入（插入）：`{"path","offset","bytes_inserted","new_size"}`
- 行索引构建：`{"path","index_path","entries","step"}`
- 偏移到行号：`{"line","scanned_bytes","from_checkpoint"}`
- 搜索（regex/literal）：`{"matches":[{...}],"count"}`
- 倒排索引构建：`{"db_path","mode","indexed_bytes"}`
- 倒排查询：`{"matches":[{...}],"count"}`

## 错误
- 文件不存在：抛出 `FileNotFoundError`
- 参数非法：断言或抛出相应异常
- 并发写：通过锁保护，超时抛出 `TimeoutError`