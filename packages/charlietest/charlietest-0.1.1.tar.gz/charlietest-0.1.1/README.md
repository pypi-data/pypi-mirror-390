# brain-test

一个使用 src 布局的示例包，包名为 `brain_test`，用于演示打包与发布到 PyPI 的最小结构。

## 安装

```bash
pip install brain-test
```

## 使用

```python
from brain_test import greet

print(greet("World"))
```

或使用示例模块：

```python
from brain_test.example import add

print(add(2, 3))  # 5
```

## 开发

- Python: 3.8+
- 构建工具: Hatchling

构建命令：

```bash
python -m build
```

发布命令：

```bash
python -m twine upload dist/*
```

## 许可证

本项目采用 MIT 协议，详见 `LICENSE`。

