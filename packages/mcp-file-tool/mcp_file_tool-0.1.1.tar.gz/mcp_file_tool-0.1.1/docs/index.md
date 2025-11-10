# MCP File Tool

一个轻量的 MCP 服务/SDK 扩展，专注于大文本文件的分片读写、流式搜索与倒排索引。

- 分片读取：按字节/按行，避免一次性读入
- 分片写入：覆盖、追加、插入（原子替换）
- 高效搜索：流式正则与字面量搜索，返回偏移/近似行号/上下文
- 行索引：每 N 行记录偏移，加速行定位
- 倒排索引：SQLite 存储，支持精确与前缀查询
- 返回结构：统一采用 `TypedDict` 类型，便于解析与静态检查
- 上下文：所有工具支持可选 `ctx` 参数用于日志追踪，不影响功能

## 安装
```bash
pip install mcp-file-tool
```

## 命令行
```bash
mcp-file-tool  # 以 STDIO 启动 MCP 服务
```

## 集成
- Trae / Claude Desktop：配置为 STDIO MCP 服务器即可
- 详见使用指南与 API 文档