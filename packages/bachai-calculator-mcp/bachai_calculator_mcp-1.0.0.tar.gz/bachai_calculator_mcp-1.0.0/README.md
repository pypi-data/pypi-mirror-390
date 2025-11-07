# Calculator MCP

一个简单而强大的计算器 MCP 服务器，通过 Model Context Protocol 提供数学运算功能。

## 功能特性

- ➕ **基本运算**: 加、减、乘、除、幂、取模
- 🔢 **高级数学**: 平方根、阶乘、对数
- 📐 **三角函数**: sin、cos、tan
- 🚀 **零依赖**: 仅使用 Python 标准库
- 📡 **stdio 模式**: 兼容 supergateway 和 Claude Desktop

## 快速开始

### 使用 uvx (推荐)

```bash
uvx bachai-calculator-mcp
```

### 使用 pip 安装

```bash
pip install bachai-calculator-mcp
bachai-calculator-mcp
```

### 直接运行

```bash
python main.py
```

## MCP 工具列表

### 1. calculate
基本数学运算

**参数**:
- `operation`: 运算类型（add, subtract, multiply, divide, power, modulo）
- `a`: 第一个数字
- `b`: 第二个数字

**示例**:
```json
{
  "name": "calculate",
  "arguments": {
    "operation": "add",
    "a": 10,
    "b": 5
  }
}
```
**返回**: `10 + 5 = 15`

### 2. sqrt
计算平方根

**参数**:
- `number`: 要计算平方根的数字

**示例**:
```json
{
  "name": "sqrt",
  "arguments": {
    "number": 16
  }
}
```
**返回**: `√16 = 4.0`

### 3. factorial
计算阶乘

**参数**:
- `number`: 要计算阶乘的整数

**示例**:
```json
{
  "name": "factorial",
  "arguments": {
    "number": 5
  }
}
```
**返回**: `5! = 120`

### 4. trigonometry
三角函数计算

**参数**:
- `function`: 三角函数类型（sin, cos, tan）
- `angle`: 角度（度数）

**示例**:
```json
{
  "name": "trigonometry",
  "arguments": {
    "function": "sin",
    "angle": 30
  }
}
```
**返回**: `sin(30°) = 0.5`

### 5. logarithm
对数计算

**参数**:
- `number`: 真数
- `base`: 底数（可选，默认为 e）

**示例**:
```json
{
  "name": "logarithm",
  "arguments": {
    "number": 100,
    "base": 10
  }
}
```
**返回**: `log_10(100) = 2.0`

## 配置

### Supergateway 配置

```json
{
  "mcpServers": {
    "calculator": {
      "outputTransport": "sse",
      "port": 8000,
      "stdio": "uvx bachai-calculator-mcp",
      "ssePath": "/sse",
      "messagePath": "/message"
    }
  }
}
```

### Claude Desktop 配置

Windows: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uvx",
      "args": ["bachai-calculator-mcp"]
    }
  }
}
```

macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "calculator": {
      "command": "uvx",
      "args": ["bachai-calculator-mcp"]
    }
  }
}
```

## 使用示例

### 在 Claude Desktop 中使用

安装并配置后，您可以向 Claude 发送类似的请求：

- "请帮我计算 123 + 456"
- "计算 25 的平方根"
- "5 的阶乘是多少？"
- "计算 sin(45度)"
- "计算以 2 为底 8 的对数"

### 手动测试

```bash
# 测试初始化
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | uvx bachai-calculator-mcp

# 测试加法
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"calculate","arguments":{"operation":"add","a":10,"b":5}}}' | uvx bachai-calculator-mcp
```

## 技术特点

- **零依赖**: 仅使用 Python 标准库（math, operator, json）
- **轻量级**: 代码简洁，启动快速
- **可靠**: 完整的错误处理和边界检查
- **兼容性**: 支持 Python 3.7+
- **标准化**: 完全遵循 MCP 协议规范

## 错误处理

服务器包含完善的错误处理：

- ✅ 除零检查
- ✅ 负数平方根检查
- ✅ 阶乘范围验证
- ✅ 对数参数验证
- ✅ JSON 解析错误处理

## 开发

```bash
# 克隆仓库
git clone https://github.com/BACH-AI-Tools/calculator-mcp.git
cd calculator-mcp

# 本地测试
python main.py

# 构建包
python -m build

# 发布到 PyPI
python -m twine upload dist/*
```

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issue 和 Pull Request！

## 更新日志

### v1.0.0 (2024-11-07)
- 🎉 初始发布
- ✨ 支持基本数学运算
- ✨ 支持高级数学函数
- ✨ 支持三角函数
- ✨ 零依赖实现

