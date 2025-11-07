# Data Analysis MCP (Python)

一个基于 Model Context Protocol 的数据分析服务器，使用 Python 开发，支持 **SSE (Server-Sent Events)** 传输模式。

## 功能特性

- 📊 数据统计分析（均值、中位数、标准差等）
- 📈 数据可视化（生成图表）
- 🔍 数据探索（查看数据摘要、缺失值等）
- 📉 趋势分析
- 📋 支持 CSV、Excel、JSON 等格式
- 🌐 基于 HTTP/SSE 的远程访问
- 🚀 RESTful API 接口

## 技术栈

- Python 3.8+
- FastAPI - 现代化 Web 框架
- SSE-Starlette - Server-Sent Events 支持
- Uvicorn - ASGI 服务器
- pandas - 数据分析
- numpy - 数值计算
- matplotlib - 数据可视化
- seaborn - 统计图表

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行服务器

#### 方式 1: stdio 模式（用于 supergateway/Claude Desktop）

```bash
# 使用 uvx (推荐)
uvx bachai-data-analysis-mcp

# 或使用 pip 安装后运行
pip install bachai-data-analysis-mcp
bachai-data-analysis-mcp
```

stdio 模式通过标准输入输出进行通信，适合与 supergateway 或 Claude Desktop 集成。

#### 方式 2: SSE 模式（独立 HTTP 服务器）

```bash
# 直接运行
python main.py

# 或使用命令
bachai-data-analysis-mcp-sse
```

服务器将在 `http://localhost:8000` 启动。

### 访问 API 文档

启动后访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API 端点

### 1. 根端点
```
GET http://localhost:8000/
```
返回服务器信息和可用端点

### 2. SSE 连接端点
```
GET http://localhost:8000/sse
```
建立 Server-Sent Events 连接，接收服务器推送的消息

### 3. 消息处理端点
```
POST http://localhost:8000/messages
Content-Type: application/json
```
发送 MCP JSON-RPC 请求

#### 示例请求：

**初始化**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {}
}
```

**列出工具**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/list",
  "params": {}
}
```

**调用工具**
```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "load_data",
    "arguments": {
      "filepath": "data.csv",
      "dataset_name": "my_data"
    }
  }
}
```

## MCP 工具列表

### 1. load-data
加载数据文件
- 支持 CSV、Excel、JSON 格式

### 2. describe-data
获取数据摘要统计
- 行列数
- 数据类型
- 缺失值统计
- 基本统计量

### 3. analyze-column
分析特定列的数据
- 唯一值数量
- 频率分布
- 数值统计

### 4. correlation-analysis
相关性分析
- 计算变量间相关系数
- 生成相关性矩阵

### 5. list-datasets
列出已加载的数据集
- 显示所有数据集
- 查看数据集基本信息

## 使用示例

### 使用 curl 测试

**1. 列出可用工具**
```bash
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

**2. 加载数据**
```bash
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "load_data",
      "arguments": {
        "filepath": "data.csv",
        "dataset_name": "sales"
      }
    }
  }'
```

**3. 获取数据描述**
```bash
curl -X POST http://localhost:8000/messages \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 3,
    "method": "tools/call",
    "params": {
      "name": "describe_data",
      "arguments": {
        "dataset_name": "sales"
      }
    }
  }'
```

### 在 Claude Desktop 中配置

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "data-analysis": {
      "url": "http://localhost:8000/sse",
      "transport": "sse"
    }
  }
}
```

## 开发

### 启动开发服务器
```bash
python main.py
```

### 运行测试
```bash
pytest tests/
```

## 许可证

MIT

