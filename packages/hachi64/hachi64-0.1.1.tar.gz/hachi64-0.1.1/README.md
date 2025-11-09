# Hachi64 for Python

哈吉米64 编解码器的 Python 实现 - 使用64个中文字符进行 Base64 风格的编码和解码。

## 特性

- 使用固定的哈吉米64字符集（64个中文字符）
- 支持带填充和不带填充两种模式
- 提供多种调用方式（实例方法、静态方法、便捷函数）
- 完全符合 Base64 编码标准
- 零依赖（仅测试依赖）
- 完整的类型注解支持
- 兼容 Python 3.6+

## 安装

```bash
pip install hachi64
```

## 快速开始

### 基本用法

```python
from hachi64 import hachi64, Hachi64, encode, decode

# 方式 1: 使用默认实例（推荐）
encoded = hachi64.encode(b"Hello")
print(f"编码结果: {encoded}")  # 豆米啊拢嘎米多=

decoded = hachi64.decode(encoded)
print(f"解码结果: {decoded.decode('utf-8')}")  # Hello

# 方式 2: 使用类静态方法
encoded = Hachi64.encode(b"Hello")
decoded = Hachi64.decode(encoded)

# 方式 3: 使用便捷函数（如果导出）
# encoded = encode(b"Hello")
# decoded = decode(encoded)
```

### 字符串编码解码

```python
from hachi64 import hachi64

# 编码字符串
text = "Hello, World!"
encoded = hachi64.encode(text.encode('utf-8'))
print(f"编码结果: {encoded}")

# 解码回字符串
decoded_bytes = hachi64.decode(encoded)
decoded_text = decoded_bytes.decode('utf-8')
print(f"解码结果: {decoded_text}")
```

### 不使用填充

```python
from hachi64 import hachi64

data = b"Hello"
encoded = hachi64.encode(data, padding=False)
print(encoded)  # 豆米啊拢嘎米多（无填充符号=）

decoded = hachi64.decode(encoded, padding=False)
print(decoded.decode('utf-8'))  # Hello
```

### 二进制数据处理

```python
from hachi64 import hachi64

# 编码任意二进制数据
binary_data = bytes(range(256))
encoded = hachi64.encode(binary_data)

# 解码回二进制
decoded = hachi64.decode(encoded)
assert decoded == binary_data  # 完全一致
```

## 编码示例

根据主 README 文档中的示例：

| 原始数据 | 编码结果 |
|---------|---------|
| `"Hello"` | `豆米啊拢嘎米多=` |
| `"abc"` | `西阿南呀` |
| `"a"` | `西律==` |
| `"ab"` | `西阿迷=` |
| `"Python"` | `抖咪酷丁息米都慢` |
| `"Hello, World!"` | `豆米啊拢嘎米多拢迷集伽漫咖苦播库迷律==` |
| `"Base64"` | `律苦集叮希斗西丁` |
| `"Hachi64"` | `豆米集呀息米库咚背哈==` |

## API 文档

### 类：Hachi64

哈吉米64编码器/解码器类。

#### 静态方法

##### `encode(data: bytes, padding: bool = True) -> str`

将字节数组编码为哈吉米64字符串。

**参数:**
- `data`: 要编码的字节数据
- `padding`: 是否使用 `=` 进行填充（默认：`True`）

**返回:**
- 编码后的字符串

**示例:**
```python
encoded = Hachi64.encode(b"Hello")
print(encoded)  # 豆米啊拢嘎米多=
```

##### `decode(encoded_str: str, padding: bool = True) -> bytes`

将哈吉米64字符串解码为字节数组。

**参数:**
- `encoded_str`: 要解码的字符串
- `padding`: 输入字符串是否使用 `=` 进行填充（默认：`True`）

**返回:**
- 解码后的字节数组

**异常:**
- `ValueError`: 如果输入字符串包含无效字符

**示例:**
```python
decoded = Hachi64.decode("豆米啊拢嘎米多=")
print(decoded.decode('utf-8'))  # Hello
```

### 实例：hachi64

默认的 `Hachi64` 实例，提供便捷访问。

**示例:**
```python
from hachi64 import hachi64

# 使用默认实例
encoded = hachi64.encode(b"Python")
decoded = hachi64.decode(encoded)
```

### 常量

#### `HACHI_ALPHABET`

哈吉米64字符集，包含64个中文字符：

```python
哈蛤呵吉急集米咪迷南男难北背杯绿律虑豆斗抖啊阿额西希息嘎咖伽花华哗压鸭呀库酷苦奶乃耐龙隆拢曼慢漫波播玻叮丁订咚东冬囊路陆多都弥济
```

## 使用示例

### 完整示例程序

创建一个 `example.py` 文件：

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from hachi64 import hachi64, HACHI_ALPHABET

def main():
    print("=== 哈吉米64 编解码示例 ===\n")
    
    # 示例 1: 基本编码解码
    print("1. 基本编码解码:")
    text = "Hello, World!"
    data = text.encode('utf-8')
    encoded = hachi64.encode(data)
    decoded = hachi64.decode(encoded)
    
    print(f"   原始文本: {text}")
    print(f"   编码结果: {encoded}")
    print(f"   解码结果: {decoded.decode('utf-8')}\n")
    
    # 示例 2: 不使用填充
    print("2. 不使用填充:")
    text = "Python"
    data = text.encode('utf-8')
    encoded_no_pad = hachi64.encode(data, padding=False)
    decoded_no_pad = hachi64.decode(encoded_no_pad, padding=False)
    
    print(f"   原始文本: {text}")
    print(f"   编码结果: {encoded_no_pad}")
    print(f"   解码结果: {decoded_no_pad.decode('utf-8')}\n")
    
    # 示例 3: 二进制数据
    print("3. 二进制数据:")
    binary_data = bytes([0x48, 0x61, 0x63, 0x68, 0x69])
    encoded_bin = hachi64.encode(binary_data)
    decoded_bin = hachi64.decode(encoded_bin)
    
    print(f"   原始数据: {binary_data.hex()}")
    print(f"   编码结果: {encoded_bin}")
    print(f"   解码数据: {decoded_bin.hex()}")
    print(f"   数据一致: {binary_data == decoded_bin}\n")
    
    # 示例 4: 显示字符集
    print("4. 哈吉米64字符集:")
    print(f"   字符总数: {len(HACHI_ALPHABET)}")
    print(f"   字符集: {HACHI_ALPHABET}\n")

if __name__ == "__main__":
    main()
```

运行示例：

```bash
python example.py
```

## 开发

### 运行测试

```bash
cd python
python -m pytest tests/
```

或使用 unittest：

```bash
python -m unittest discover tests
```

### 测试覆盖率

```bash
pip install pytest pytest-cov
pytest --cov=hachi64 tests/
```

## 兼容性

- **Python 版本**: 3.6 或更高
- **依赖**: 无运行时依赖
- **编码**: 完全支持 UTF-8

## 性能说明

Python 实现使用纯 Python 代码，提供良好的可读性和可维护性。对于大规模数据处理，建议考虑：

- 使用批处理方式处理多个小数据
- 对性能敏感场景可考虑 Rust 或 C++ 实现
- 对于 Web 应用，JavaScript/TypeScript 实现可能更合适

## 与标准 Base64 的对比

| 特性 | 标准 Base64 | 哈吉米64 |
|-----|-----------|---------|
| 字符集 | A-Za-z0-9+/ | 64个中文字符 |
| 编码长度 | 相同 | 相同 |
| 填充字符 | = | = |
| 兼容性 | 标准实现 | 自定义实现 |
| 用途 | 通用编码 | 特殊场景/艺术效果 |

## 常见问题

### Q: 为什么使用中文字符？

A: 哈吉米64使用发音相似的中文字符分组，使编码结果具有独特的视觉和听觉效果。这是一个艺术化的编码方案。

### Q: 可以与标准 Base64 互换使用吗？

A: 不可以。哈吉米64使用自定义字符集，编码结果只能用哈吉米64解码器解码。

### Q: 性能如何？

A: Python 实现适合中小规模数据处理。对于大规模或高性能需求，建议使用 Rust、Go 或 C++ 实现。

### Q: 如何处理错误？

A: 解码时如果遇到无效字符，会抛出 `ValueError` 异常。建议使用 try-except 捕获处理。

```python
try:
    decoded = hachi64.decode(some_string)
except ValueError as e:
    print(f"解码错误: {e}")
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [主项目仓库](https://github.com/fengb3/Hachi64)
- [在线文档](https://github.com/fengb3/Hachi64/tree/main/docs)
- [其他语言实现](https://github.com/fengb3/Hachi64#多语言支持)
