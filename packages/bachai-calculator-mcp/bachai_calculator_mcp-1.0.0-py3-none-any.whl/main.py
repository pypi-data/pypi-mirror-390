#!/usr/bin/env python3
"""
计算器 MCP 服务器 - 提供基本数学运算功能
"""

import json
import sys
from typing import Any, Dict
import math
import operator

# 延迟导入（如果需要 FastAPI）
def _lazy_imports_sse():
    """延迟导入 SSE 模式所需的库"""
    global FastAPI, Request, Response, JSONResponse, uvicorn
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import JSONResponse
    import uvicorn


class CalculatorMcpServer:
    def __init__(self):
        self.server_info = {
            "name": "calculator-mcp",
            "version": "1.0.0"
        }
        
        # 支持的运算符
        self.operators = {
            "add": operator.add,
            "subtract": operator.sub,
            "multiply": operator.mul,
            "divide": operator.truediv,
            "power": operator.pow,
            "modulo": operator.mod,
        }
    
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """处理请求"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = self.handle_initialize()
            elif method == "tools/list":
                result = self.handle_list_tools()
            elif method == "tools/call":
                result = self.handle_tool_call(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
    
    def handle_initialize(self) -> Dict[str, Any]:
        """处理初始化"""
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": self.server_info,
            "capabilities": {
                "tools": {}
            }
        }
    
    def handle_list_tools(self) -> Dict[str, Any]:
        """列出可用工具"""
        return {
            "tools": [
                {
                    "name": "calculate",
                    "description": "执行基本数学运算（加、减、乘、除、幂、取模）",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": ["add", "subtract", "multiply", "divide", "power", "modulo"],
                                "description": "运算类型"
                            },
                            "a": {
                                "type": "number",
                                "description": "第一个数字"
                            },
                            "b": {
                                "type": "number",
                                "description": "第二个数字"
                            }
                        },
                        "required": ["operation", "a", "b"]
                    }
                },
                {
                    "name": "sqrt",
                    "description": "计算平方根",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "number": {
                                "type": "number",
                                "description": "要计算平方根的数字"
                            }
                        },
                        "required": ["number"]
                    }
                },
                {
                    "name": "factorial",
                    "description": "计算阶乘",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "number": {
                                "type": "integer",
                                "description": "要计算阶乘的整数"
                            }
                        },
                        "required": ["number"]
                    }
                },
                {
                    "name": "trigonometry",
                    "description": "三角函数计算（sin、cos、tan）",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "function": {
                                "type": "string",
                                "enum": ["sin", "cos", "tan"],
                                "description": "三角函数类型"
                            },
                            "angle": {
                                "type": "number",
                                "description": "角度（度数）"
                            }
                        },
                        "required": ["function", "angle"]
                    }
                },
                {
                    "name": "logarithm",
                    "description": "对数计算",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "number": {
                                "type": "number",
                                "description": "真数"
                            },
                            "base": {
                                "type": "number",
                                "description": "底数（可选，默认为 e）"
                            }
                        },
                        "required": ["number"]
                    }
                }
            ]
        }
    
    def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        try:
            if tool_name == "calculate":
                result = self.calculate(args)
            elif tool_name == "sqrt":
                result = self.sqrt(args)
            elif tool_name == "factorial":
                result = self.factorial(args)
            elif tool_name == "trigonometry":
                result = self.trigonometry(args)
            elif tool_name == "logarithm":
                result = self.logarithm(args)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"错误: {str(e)}"
                    }
                ]
            }
    
    def calculate(self, args: Dict[str, Any]) -> str:
        """基本数学运算"""
        operation = args.get("operation")
        a = args.get("a")
        b = args.get("b")
        
        if operation not in self.operators:
            return f"错误: 不支持的运算 '{operation}'"
        
        try:
            if operation == "divide" and b == 0:
                return "错误: 除数不能为零"
            
            result = self.operators[operation](a, b)
            
            op_symbols = {
                "add": "+",
                "subtract": "-",
                "multiply": "×",
                "divide": "÷",
                "power": "^",
                "modulo": "%"
            }
            
            return f"{a} {op_symbols[operation]} {b} = {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    def sqrt(self, args: Dict[str, Any]) -> str:
        """计算平方根"""
        number = args.get("number")
        
        if number < 0:
            return "错误: 不能计算负数的平方根"
        
        result = math.sqrt(number)
        return f"√{number} = {result}"
    
    def factorial(self, args: Dict[str, Any]) -> str:
        """计算阶乘"""
        number = args.get("number")
        
        if number < 0:
            return "错误: 不能计算负数的阶乘"
        
        if number > 170:
            return "错误: 数字太大，无法计算阶乘"
        
        result = math.factorial(number)
        return f"{number}! = {result}"
    
    def trigonometry(self, args: Dict[str, Any]) -> str:
        """三角函数计算"""
        function = args.get("function")
        angle = args.get("angle")
        
        # 将角度转换为弧度
        radians = math.radians(angle)
        
        if function == "sin":
            result = math.sin(radians)
        elif function == "cos":
            result = math.cos(radians)
        elif function == "tan":
            result = math.tan(radians)
        else:
            return f"错误: 不支持的三角函数 '{function}'"
        
        return f"{function}({angle}°) = {result}"
    
    def logarithm(self, args: Dict[str, Any]) -> str:
        """对数计算"""
        number = args.get("number")
        base = args.get("base")
        
        if number <= 0:
            return "错误: 真数必须大于 0"
        
        if base is None:
            # 自然对数
            result = math.log(number)
            return f"ln({number}) = {result}"
        else:
            if base <= 0 or base == 1:
                return "错误: 底数必须大于 0 且不等于 1"
            
            result = math.log(number, base)
            return f"log_{base}({number}) = {result}"


def main_stdio():
    """stdio 模式入口点（用于 supergateway/Claude Desktop）"""
    import traceback
    
    print("🧮 启动 Calculator MCP Server (stdio 模式)", file=sys.stderr)
    print("📥 等待来自 stdin 的 JSON-RPC 请求...", file=sys.stderr)
    
    # 创建服务器实例
    try:
        server = CalculatorMcpServer()
        print("✅ 服务器实例创建成功", file=sys.stderr)
    except Exception as e:
        print(f"❌ 服务器实例创建失败: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
    
    # 从 stdin 读取请求，向 stdout 发送响应
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            print(f"📨 收到请求: {line[:100]}...", file=sys.stderr)
            
            try:
                request = json.loads(line)
                print(f"🔄 处理方法: {request.get('method')}", file=sys.stderr)
                
                response = server.handle_request(request)
                response_json = json.dumps(response)
                
                print(response_json, flush=True)
                print(f"✅ 响应已发送", file=sys.stderr)
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON 解析错误: {e}", file=sys.stderr)
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
            except Exception as e:
                print(f"❌ 处理请求时出错: {e}", file=sys.stderr)
                traceback.print_exc(file=sys.stderr)
                error_response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                print(json.dumps(error_response), flush=True)
                
    except KeyboardInterrupt:
        print("⏹️  服务器被中断", file=sys.stderr)
    except Exception as e:
        print(f"❌ 致命错误: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


def main():
    """主入口点 - 默认使用 stdio 模式"""
    main_stdio()


if __name__ == "__main__":
    main_stdio()

