# Windows 兼容性修复总结

## 问题
项目原本依赖 Unix/Linux 特定的模块（`tty` 和 `termios`），无法在 Windows 上运行。

## 解决方案

### 1. 添加跨平台依赖 (pyproject.toml)
```
readchar>=4.0.0
```
`readchar` 是一个跨平台库，内部自动处理 Windows/macOS/Linux 的差异。

### 2. 重构 `input_handler.py`
**移除的内容：**
- `import tty` - Unix 特定
- `import termios` - Unix 特定
- 手动的终端属性管理代码

**新增内容：**
- `import readchar` - 跨平台库
- 条件导入 `termios`（有防护）
- 改进的按键映射，支持 Enter 键的两种表示（\r 和 \n）

**关键改进：**
```python
# 支持两种 Enter 键表示
elif ch == InputHandler._READCHAR_ENTER_CR or ch == InputHandler._READCHAR_ENTER_LF:
    return InputHandler.ENTER
```

### 3. 增强 `terminal.py`
- 改进 `get_terminal_size()` 方法的错误处理
- 添加回退方案（默认 80x24）
- 保持 `clear_screen()` 的平台检测逻辑

## 兼容性
现在支持：
- ✅ **Windows** (Python 3.3+)
- ✅ **macOS** (10.9+)
- ✅ **Linux** (所有主流发行版)

## API 兼容性
所有公共 API 完全兼容，现有代码无需改动。

## 测试
运行以下命令验证：
```bash
python test_windows_compatibility.py
```

## 关键文件修改
- `pyproject.toml` - 添加 readchar 依赖
- `promptabs/input_handler.py` - 完全重构为跨平台实现
- `promptabs/terminal.py` - 增强错误处理

## 注意
- `readchar` 库会自动在 Windows 上使用 `msvcrt`
- 在 Unix/Linux 上仍使用 `termios`（但现在由 `readchar` 内部管理）
- 所有键盘输入都通过统一的 `InputHandler.read_single_key()` 接口
