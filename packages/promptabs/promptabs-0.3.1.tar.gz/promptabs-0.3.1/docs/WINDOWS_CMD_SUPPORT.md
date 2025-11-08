# Windows cmd.exe 支持

## 问题

Windows cmd.exe 使用与 Unix/Linux/macOS 不同的按键编码：

- **Unix/Linux/macOS**: `ESC [ A` (up), `ESC [ B` (down) 等
- **Windows cmd.exe**: `\x00 H` 或 `\xe0 H` (up), `\x00 P` 或 `\xe0 P` (down) 等

## 解决方案

已在 `promptabs/input_handler.py` 中添加 Windows 特殊按键处理：

```python
# Windows special key indicators
_WINDOWS_SPECIAL_KEY_1 = "\x00"  # First null byte (older Windows)
_WINDOWS_SPECIAL_KEY_2 = "\xe0"  # Extended key code (modern Windows)

# Windows arrow key codes
_WINDOWS_ARROW_UP = "H"
_WINDOWS_ARROW_DOWN = "P"
_WINDOWS_ARROW_LEFT = "K"
_WINDOWS_ARROW_RIGHT = "M"
```

当检测到 Windows 特殊键时，读取第二个字节并映射到箭头键。

## 测试

### 在 Windows cmd.exe 上测试

```bash
# 安装包
uv pip install -e .

# 运行测试脚本
python test_windows_keys.py
```

按上下左右箭头，应该看到：
```
1. ✓ UP ARROW detected!
2. ✓ DOWN ARROW detected!
3. ✓ LEFT ARROW detected!
4. ✓ RIGHT ARROW detected!
```

### 运行主程序

```bash
# 直接运行
demo

# 或使用 python -m
python -m promptabs

# 或运行示例
python examples/simple_survey.py
```

现在上下箭头应该能正常工作了！

## 诊断

如果箭头键仍然不工作，运行诊断脚本：

```bash
python diagnose_windows.py
```

这会显示 Windows 上实际返回的按键代码，帮助我们进一步调试。

## 兼容性

现在支持：
- ✅ Windows 10+ (cmd.exe)
- ✅ Windows 7/8 (cmd.exe)
- ✅ macOS (all versions)
- ✅ Linux (all distros)
- ✅ PowerShell (Windows)
