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