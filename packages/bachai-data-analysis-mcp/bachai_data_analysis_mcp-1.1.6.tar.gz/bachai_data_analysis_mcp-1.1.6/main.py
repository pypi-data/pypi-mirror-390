#!/usr/bin/env python3
"""
数据分析 MCP 服务器 - stdio 和 SSE 双模式
"""

import json
import sys
from typing import Any, Dict, Optional
from pathlib import Path

# 延迟导入：只在需要时导入重型库
def _lazy_imports():
    """延迟导入所有数据分析相关的库"""
    global pd, np, plt, sns
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns

# 延迟导入：只在 SSE 模式时导入 FastAPI 相关库
def _lazy_imports_sse():
    """延迟导入 SSE 模式所需的库"""
    global FastAPI, Request, Response, StreamingResponse, JSONResponse
    global CORSMiddleware, EventSourceResponse, uvicorn, asyncio, uuid
    from fastapi import FastAPI, Request, Response
    from fastapi.responses import StreamingResponse, JSONResponse
    from fastapi.middleware.cors import CORSMiddleware
    from sse_starlette.sse import EventSourceResponse
    import uvicorn
    import asyncio
    import uuid

# 存储加载的数据集
loaded_datasets: Dict[str, Any] = {}

# 存储待处理的消息队列（用于 SSE 通信）
message_queues: Dict[str, Any] = {}
response_queues: Dict[str, Any] = {}

# FastAPI app 将在 SSE 模式下初始化
app = None


class DataAnalysisMcpServer:
    def __init__(self):
        # 确保数据分析库已导入
        _lazy_imports()
        
        self.server_info = {
            "name": "data-analysis-mcp",
            "version": "1.1.6"
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
                    "name": "load_data",
                    "description": "加载数据文件（支持CSV、Excel、JSON）",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "filepath": {
                                "type": "string",
                                "description": "数据文件路径"
                            },
                            "dataset_name": {
                                "type": "string",
                                "description": "数据集名称（用于后续引用）"
                            },
                            "file_type": {
                                "type": "string",
                                "description": "文件类型（csv/excel/json，可选，自动检测）"
                            }
                        },
                        "required": ["filepath"]
                    }
                },
                {
                    "name": "describe_data",
                    "description": "获取数据集的描述性统计信息",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "dataset_name": {
                                "type": "string",
                                "description": "数据集名称"
                            }
                        },
                        "required": ["dataset_name"]
                    }
                },
                {
                    "name": "analyze_column",
                    "description": "分析特定列的数据",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "dataset_name": {
                                "type": "string",
                                "description": "数据集名称"
                            },
                            "column_name": {
                                "type": "string",
                                "description": "列名"
                            }
                        },
                        "required": ["dataset_name", "column_name"]
                    }
                },
                {
                    "name": "correlation_analysis",
                    "description": "计算数值列之间的相关性",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "dataset_name": {
                                "type": "string",
                                "description": "数据集名称"
                            }
                        },
                        "required": ["dataset_name"]
                    }
                },
                {
                    "name": "list_datasets",
                    "description": "列出已加载的数据集",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    def handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """处理工具调用"""
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        try:
            if tool_name == "load_data":
                result = self.load_data(args)
            elif tool_name == "describe_data":
                result = self.describe_data(args)
            elif tool_name == "analyze_column":
                result = self.analyze_column(args)
            elif tool_name == "correlation_analysis":
                result = self.correlation_analysis(args)
            elif tool_name == "list_datasets":
                result = self.list_datasets(args)
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
    
    def load_data(self, args: Dict[str, Any]) -> str:
        """加载数据文件"""
        filepath = args.get("filepath")
        dataset_name = args.get("dataset_name", "default")
        file_type = args.get("file_type")
        
        path = Path(filepath)
        if not path.exists():
            return f"错误: 文件不存在 - {filepath}"
        
        try:
            # 自动检测文件类型
            if file_type is None:
                ext = path.suffix.lower()
                if ext == '.csv':
                    file_type = 'csv'
                elif ext in ['.xlsx', '.xls']:
                    file_type = 'excel'
                elif ext == '.json':
                    file_type = 'json'
                else:
                    return f"错误: 不支持的文件类型 - {ext}"
            
            # 加载数据
            if file_type == 'csv':
                df = pd.read_csv(filepath)
            elif file_type == 'excel':
                df = pd.read_excel(filepath)
            elif file_type == 'json':
                df = pd.read_json(filepath)
            else:
                return f"错误: 不支持的文件类型 - {file_type}"
            
            loaded_datasets[dataset_name] = df
            
            output = f"=== 数据加载成功 ===\n"
            output += f"数据集名称: {dataset_name}\n"
            output += f"文件路径: {filepath}\n"
            output += f"行数: {len(df)}\n"
            output += f"列数: {len(df.columns)}\n"
            output += f"列名: {', '.join(df.columns.tolist())}\n"
            output += f"\n前5行数据:\n{df.head().to_string()}\n"
            
            return output
        except Exception as e:
            return f"错误: 加载数据失败 - {str(e)}"
    
    def describe_data(self, args: Dict[str, Any]) -> str:
        """描述性统计"""
        dataset_name = args.get("dataset_name")
        
        if dataset_name not in loaded_datasets:
            return f"错误: 数据集 '{dataset_name}' 未加载"
        
        df = loaded_datasets[dataset_name]
        
        output = f"=== 数据集描述: {dataset_name} ===\n\n"
        output += f"形状: {df.shape[0]} 行 × {df.shape[1]} 列\n\n"
        
        # 数据类型
        output += "列信息:\n"
        for col in df.columns:
            output += f"  {col}: {df[col].dtype}\n"
        
        # 缺失值
        missing = df.isnull().sum()
        if missing.sum() > 0:
            output += f"\n缺失值:\n"
            for col, count in missing.items():
                if count > 0:
                    output += f"  {col}: {count} ({count/len(df)*100:.2f}%)\n"
        else:
            output += f"\n无缺失值\n"
        
        # 数值列统计
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            output += f"\n数值列统计:\n"
            output += df[numeric_cols].describe().to_string()
        
        # 分类列统计
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            output += f"\n\n分类列统计:\n"
            for col in categorical_cols[:5]:  # 只显示前5个
                output += f"\n{col}:\n"
                output += f"  唯一值数: {df[col].nunique()}\n"
                value_counts = df[col].value_counts().head(5)
                output += f"  前5个值:\n"
                for val, count in value_counts.items():
                    output += f"    {val}: {count}\n"
        
        return output
    
    def analyze_column(self, args: Dict[str, Any]) -> str:
        """分析特定列"""
        dataset_name = args.get("dataset_name")
        column_name = args.get("column_name")
        
        if dataset_name not in loaded_datasets:
            return f"错误: 数据集 '{dataset_name}' 未加载"
        
        df = loaded_datasets[dataset_name]
        
        if column_name not in df.columns:
            return f"错误: 列 '{column_name}' 不存在"
        
        col = df[column_name]
        
        output = f"=== 列分析: {column_name} ===\n\n"
        output += f"数据类型: {col.dtype}\n"
        output += f"总数: {len(col)}\n"
        output += f"缺失值: {col.isnull().sum()} ({col.isnull().sum()/len(col)*100:.2f}%)\n"
        output += f"唯一值: {col.nunique()}\n\n"
        
        if pd.api.types.is_numeric_dtype(col):
            # 数值型列
            output += "统计量:\n"
            output += f"  均值: {col.mean():.4f}\n"
            output += f"  中位数: {col.median():.4f}\n"
            output += f"  标准差: {col.std():.4f}\n"
            output += f"  最小值: {col.min():.4f}\n"
            output += f"  最大值: {col.max():.4f}\n"
            output += f"  25%分位数: {col.quantile(0.25):.4f}\n"
            output += f"  75%分位数: {col.quantile(0.75):.4f}\n"
        else:
            # 分类型列
            output += "值频率（前10）:\n"
            value_counts = col.value_counts().head(10)
            for val, count in value_counts.items():
                output += f"  {val}: {count} ({count/len(col)*100:.2f}%)\n"
        
        return output
    
    def correlation_analysis(self, args: Dict[str, Any]) -> str:
        """相关性分析"""
        dataset_name = args.get("dataset_name")
        
        if dataset_name not in loaded_datasets:
            return f"错误: 数据集 '{dataset_name}' 未加载"
        
        df = loaded_datasets[dataset_name]
        numeric_cols = df.select_dtypes(include=[np.number])
        
        if numeric_cols.shape[1] < 2:
            return "错误: 至少需要2个数值列才能进行相关性分析"
        
        corr_matrix = numeric_cols.corr()
        
        output = f"=== 相关性分析: {dataset_name} ===\n\n"
        output += "相关系数矩阵:\n"
        output += corr_matrix.to_string()
        
        # 找出强相关的列对
        output += "\n\n强相关列对（|r| > 0.7）:\n"
        strong_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_val = corr_matrix.iloc[i, j]
                if abs(corr_val) > 0.7:
                    strong_corr.append(
                        (corr_matrix.columns[i], corr_matrix.columns[j], corr_val)
                    )
        
        if strong_corr:
            for col1, col2, corr_val in sorted(strong_corr, key=lambda x: abs(x[2]), reverse=True):
                output += f"  {col1} ↔ {col2}: {corr_val:.4f}\n"
        else:
            output += "  未发现强相关的列对\n"
        
        return output
    
    def list_datasets(self, args: Dict[str, Any]) -> str:
        """列出已加载的数据集"""
        if not loaded_datasets:
            return "当前没有加载的数据集。"
        
        output = "=== 已加载的数据集 ===\n\n"
        for name, df in loaded_datasets.items():
            output += f"📊 {name}\n"
            output += f"   行数: {df.shape[0]}\n"
            output += f"   列数: {df.shape[1]}\n"
            output += f"   列名: {', '.join(df.columns.tolist()[:5])}"
            if len(df.columns) > 5:
                output += f" ... (共{len(df.columns)}列)"
            output += "\n\n"
        
        return output


def _create_sse_app():
    """创建并配置 FastAPI 应用（仅在 SSE 模式下调用）"""
    # 导入 SSE 相关库
    _lazy_imports_sse()
    _lazy_imports()  # 也需要数据分析库
    
    # 创建 FastAPI 应用
    app = FastAPI(title="Data Analysis MCP Server")
    
    # 添加 CORS 支持
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 创建服务器实例
    mcp_server = DataAnalysisMcpServer()
    
    @app.get("/")
    async def root():
        """根路径，返回服务器信息"""
        return {
            "name": "Data Analysis MCP Server",
            "version": "1.1.6",
            "transport": "SSE",
            "endpoints": {
                "sse": "/sse",
                "messages": "/message"
            }
        }
    
    @app.get("/sse")
    async def sse_endpoint(request: Request):
        """SSE 端点 - 用于建立 SSE 连接并接收服务器消息"""
        session_id = str(uuid.uuid4())
        response_queue = asyncio.Queue()
        response_queues[session_id] = response_queue
        
        async def event_generator():
            """生成 SSE 事件"""
            try:
                # 发送 endpoint 事件，告诉客户端消息发送地址
                yield {
                    "event": "endpoint",
                    "data": f"/message?sessionId={session_id}"
                }
                
                # 持续发送队列中的响应
                while True:
                    if await request.is_disconnected():
                        break
                    
                    try:
                        # 等待响应消息，带超时
                        response = await asyncio.wait_for(
                            response_queue.get(),
                            timeout=30.0
                        )
                        
                        # 发送消息事件
                        yield {
                            "event": "message",
                            "data": json.dumps(response)
                        }
                    except asyncio.TimeoutError:
                        # 超时发送心跳
                        continue
                        
            except asyncio.CancelledError:
                pass
            finally:
                # 清理会话
                if session_id in response_queues:
                    del response_queues[session_id]
        
        return EventSourceResponse(event_generator())
    
    @app.post("/message")
    async def message_endpoint(request: Request, sessionId: str = None):
        """处理 MCP 消息请求"""
        try:
            body = await request.json()
            response = mcp_server.handle_request(body)
            
            # 如果有 sessionId，通过 SSE 返回
            if sessionId and sessionId in response_queues:
                await response_queues[sessionId].put(response)
                return Response(status_code=202)  # Accepted
            
            # 否则直接返回 JSON 响应
            return JSONResponse(content=response)
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {str(e)}"
                }
            }
            
            if sessionId and sessionId in response_queues:
                await response_queues[sessionId].put(error_response)
                return Response(status_code=202)
            
            return JSONResponse(content=error_response)
    
    # 兼容旧的 /messages 端点
    @app.post("/messages")
    async def messages_endpoint(request: Request):
        """处理 MCP 消息请求（兼容端点）"""
        return await message_endpoint(request)
    
    return app


def main_stdio():
    """Main entry point for stdio mode (for supergateway/Claude Desktop)"""
    import traceback
    
    print("🚀 启动 Data Analysis MCP Server (stdio 模式)", file=sys.stderr)
    print("📥 等待来自 stdin 的 JSON-RPC 请求...", file=sys.stderr)
    
    # 创建服务器实例（不使用全局的）
    try:
        server = DataAnalysisMcpServer()
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
                print(f"✅ 响应已发送: {response_json[:100]}...", file=sys.stderr)
                
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


def main_sse():
    """Main entry point for SSE mode (standalone HTTP server)"""
    print("🚀 启动 Data Analysis MCP Server (SSE 模式)", file=sys.stderr)
    print("📡 SSE Endpoint: http://localhost:8000/sse", file=sys.stderr)
    print("📨 Messages Endpoint: http://localhost:8000/messages", file=sys.stderr)
    print("📖 API Docs: http://localhost:8000/docs", file=sys.stderr)
    
    # 创建 FastAPI 应用（这会导入所有必要的库）
    app = _create_sse_app()
    
    # uvicorn 已经在 _lazy_imports_sse() 中导入
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


def main():
    """Main entry point - defaults to stdio mode for compatibility"""
    main_stdio()


if __name__ == "__main__":
    # 当直接运行时，使用 SSE 模式
    main_sse()
