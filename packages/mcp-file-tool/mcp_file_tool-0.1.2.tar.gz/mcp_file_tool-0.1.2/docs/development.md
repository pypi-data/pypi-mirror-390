# 开发与发布

## 本地开发
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python scripts/test_all.py
```

## 打包与发布
```bash
python -m pip install build twine
python -m build
python -m twine upload dist/*
```

## 版本与日志
- 使用 `CHANGELOG.md` 记录变更
- 包版本位于 `mcp_file_tool/__init__.py::__version__`

## 文档站点
```bash
pip install mkdocs mkdocs-material
mkdocs serve
```

访问 `http://127.0.0.1:8000` 查看文档（需安装 mkdocs）。

## MCP 本地调试（本地先行）
```bash
# 使用 MCP 客户端进行交互式开发与调试
mcp dev
```
- 通过交互式调用观察入参与结构化输出，结合 `logs/mcp_file_tool.log` 验证行为。

## 工具清单校验
```bash
# 列出当前注册的工具，核对名称、描述与参数
mcp list
```

## 场景测试
- 大文件读取与搜索（>1GB），验证流式读取与内存占用。
- 写入锁竞争与超时，观察 `lock_timeout_sec` 下的重试与错误信息。
- 异常路径：不存在文件、权限不足、编码不匹配，确保错误友好且返回结构化信息。

## 持续复盘与日志分析
- 定期检查 `logs/mcp_file_tool.log`，统计工具调用频次、耗时与错误率。
- 根据未命中或错误调用案例，优化工具 `TOOL_ANNOTATIONS` 与文档说明。
- 在版本发布前后运行 `scripts/mcp_tool_audit.py` 生成审计报告并归档。