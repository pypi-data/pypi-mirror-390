# Gateway SDK 使用指南 (Agent 内部调用)

## 1. 概述

本文档面向 **Agent 内部调用 Prefab** 场景。当 Agent 需要调用其他 Prefab 时，使用本 SDK。

### 核心特性

- ✅ 简洁 API - 无需手动管理认证
- ✅ 流式响应支持
- ✅ 完整的类型提示
- ✅ 自动内部认证（X-Internal-Token）
- ✅ 文件操作支持 - 上传、下载、列出和清理文件

### 认证机制

**Agent 调用 Prefab 时**：
- ❌ 不需要 API Key
- ❌ 不需要 JWT Token
- ✅ 使用 `X-Internal-Token`（由 Gateway 自动注入到 Agent 请求头）

## 2. 安装

```bash
pip install agent-builder-gateway-sdk
```

## 3. 快速开始

### 初始化客户端（在 Agent 中）

```python
from gateway_sdk import GatewayClient
from fastapi import Depends, Header

# 定义依赖注入函数（推荐）
def get_gateway_client(
    x_internal_token: str = Header(..., alias="X-Internal-Token")
) -> GatewayClient:
    """
    获取 Gateway 客户端
    
    从请求头自动获取 X-Internal-Token（Gateway 自动注入）
    """
    return GatewayClient(internal_token=x_internal_token)

# 在端点中使用
@app.post("/your-endpoint")
async def your_endpoint(
    request_data: Dict[str, Any],
    gateway_client: GatewayClient = Depends(get_gateway_client)
):
    # 直接使用 gateway_client 调用 Prefab
    result = gateway_client.run(
        prefab_id="your-prefab",
        version="1.0.0",
        function_name="your_function",
        parameters={...}
    )
```

**关键点**：
- ✅ 只需要传递 `internal_token`，`base_url` 有默认值
- ✅ `X-Internal-Token` 由 Gateway 自动注入到请求头
- ✅ 使用依赖注入，代码简洁

## 4. 调用预制件

### 基础调用

```python
# 不涉及文件的调用
result = client.run(
    prefab_id="llm-client",
    version="1.0.0",
    function_name="chat",
    parameters={"messages": [{"role": "user", "content": "Hello"}]}
)

if result.is_success():
    # 获取函数返回值
    function_result = result.get_function_result()
    print(function_result)
```

### 涉及文件的调用

```python
# 需要传递文件时，使用 S3 URL
result = client.run(
    prefab_id="video-processor",
    version="1.0.0",
    function_name="extract_audio",
    parameters={"format": "mp3"},
    files={"video": ["s3://my-bucket/input.mp4"]}
)

if result.is_success():
    # 输出文件也是 S3 URL
    output_files = result.get_files()
    print(f"输出文件: {output_files}")
```

## 5. 流式响应

```python
from gateway_sdk.models import StreamEventType

for event in client.run(..., stream=True):
    if event.type == StreamEventType.CONTENT:
        print(event.data, end="")
    elif event.type == StreamEventType.DONE:
        print("\n完成")
```

## 6. 批量调用

```python
from gateway_sdk import PrefabCall

calls = [
    PrefabCall(
        prefab_id="translator",
        version="1.0.0",
        function_name="translate",
        parameters={"text": "Hello", "target": "zh"}
    ),
    PrefabCall(
        prefab_id="translator",
        version="1.0.0",
        function_name="translate",
        parameters={"text": "World", "target": "zh"}
    )
]

result = client.run_batch(calls)
for r in result.results:
    if r.is_success():
        # 获取函数返回值
        function_result = r.get_function_result()
        print(function_result)
```

## 7. 错误处理

```python
from gateway_sdk.exceptions import (
    GatewayError,
    AuthenticationError,
    PrefabNotFoundError,
    ValidationError,
    QuotaExceededError,
    MissingSecretError,
    AgentContextRequiredError,
)

try:
    result = client.run(...)
    
except AuthenticationError as e:
    print(f"认证失败: {e}")
    
except PrefabNotFoundError as e:
    print(f"预制件不存在: {e}")
    
except MissingSecretError as e:
    print(f"缺少密钥: {e.secret_name}")
    
except QuotaExceededError as e:
    print(f"配额超限: {e.used}/{e.limit}")

except AgentContextRequiredError as e:
    print(f"需要 Agent 上下文: {e}")
    # 仅在 Agent 内部调用时才能使用文件操作
    
except GatewayError as e:
    print(f"错误: {e}")
```

## 8. API 参考

### GatewayClient

#### 初始化（Agent 内部使用）

```python
from gateway_sdk import GatewayClient
from fastapi import Header

# 依赖注入函数（推荐）
def get_gateway_client(
    x_internal_token: str = Header(..., alias="X-Internal-Token")
) -> GatewayClient:
    return GatewayClient(internal_token=x_internal_token)

# 可选：自定义超时
def get_gateway_client_with_timeout(
    x_internal_token: str = Header(..., alias="X-Internal-Token")
) -> GatewayClient:
    return GatewayClient(
        internal_token=x_internal_token,
        timeout=120  # 自定义超时（默认60秒）
    )
```

#### 方法

**run ()** - 执行单个预制件

```python
run(
    prefab_id: str,
    version: str,
    function_name: str,
    parameters: Dict[str, Any],
    files: Optional[Dict[str, List[str]]] = None,  # S3 URL 列表
    stream: bool = False
) -> Union[PrefabResult, Iterator[StreamEvent]]
```

**参数说明**：
- `prefab_id`: 预制件 ID
- `version`: 版本号
- `function_name`: 函数名
- `parameters`: 函数参数字典
- `files`: 文件输入，格式为 `{"参数名": ["s3://url1", "s3://url2"]}`，**仅接受 S 3 URL**
- `stream`: 是否使用流式响应

**run_batch ()** - 批量执行

```python
run_batch(calls: List[PrefabCall]) -> BatchResult
```

**upload_file ()** - 上传永久文件

```python
upload_file(
    file_path: str,
    content_type: Optional[str] = None
) -> str  # 返回 S3 URL
```

**upload_temp_file ()** - 上传临时文件

```python
upload_temp_file(
    file_path: str,
    content_type: Optional[str] = None,
    ttl_hours: int = 24,
    session_id: Optional[str] = None
) -> str  # 返回 S3 URL
```

**download_file ()** - 下载文件（返回预签名 URL）

```python
download_file(s3_url: str) -> str  # 返回预签名下载 URL
```

**list_files ()** - 列出永久文件

```python
list_files(prefix: Optional[str] = None) -> List[str]  # 返回 S3 URL 列表
```

**list_temp_files ()** - 列出临时文件

```python
list_temp_files(
    prefix: Optional[str] = None,
    session_id: Optional[str] = None
) -> List[str]  # 返回 S3 URL 列表
```

**cleanup_temp_files ()** - 清理临时文件

```python
cleanup_temp_files(session_id: Optional[str] = None) -> int  # 返回删除的文件数
```

**注意**：文件操作方法需要 Agent Context（通过 Gateway 调用时自动提供），在 Agent 外部使用会抛出 `AgentContextRequiredError` 异常。


### PrefabResult

```python
from typing import Dict, Any, List, Optional

class PrefabResult:
    status: CallStatus           # SUCCESS / FAILED
    output: Optional[Dict]       # 原始输出数据
    error: Optional[Dict]        # 错误信息
    job_id: Optional[str]        # 任务 ID
    
    def is_success() -> bool:
        """判断调用是否成功 (SDK层面)"""

    def get_function_result() -> Dict[str, Any]:
        """获取预制件函数的返回值 (对应 manifest.returns)"""

    def get_files() -> Dict[str, List[str]]:
        """获取输出文件字典 (对应 manifest.files)"""

    def get_file_urls() -> List[str]:
        """获取所有输出文件的 S3 URL 列表"""
```

#### 响应数据结构

**重要**：响应数据是**嵌套结构**，但您通常**不需要手动解析**，请使用下面的便捷方法。

```python
result = client.run(...)

# 完整的响应结构：
result.status          # CallStatus.SUCCESS 或 CallStatus.FAILED
result.job_id          # "933221b1-0b78-4067-b9f6-db5c3ffd2d6d"
result.output = {
    'status': 'SUCCESS',              # Gateway 层状态
    'output': {                       # ← 预制件函数的返回值（对应 manifest.returns）
        'success': True,              #    业务成功标志
        'message': '处理成功',         #    业务消息
        'data': {...},                #    业务数据
        # ... 其他字段根据预制件定义
    },
    'files': {                        # ← 输出文件（对应 manifest.files）
        'output': ['s3://...'],       #    key 对应 manifest 中的 files.key
        # ... 其他文件输出
    }
}
```

####  便捷方法 (推荐)

为简化响应解析，`PrefabResult` 提供了以下便捷方法：

**1. 获取业务数据 (函数返回值)**
```python
# ✅ 推荐: 使用 get_function_result() 直接获取
# 这对应 manifest.json 中的 returns.properties
function_result = result.get_function_result()

if function_result:
    success = function_result.get('success')  # 业务成功标志
    message = function_result.get('message')  # 业务消息
    content = function_result.get('content')  # 业务数据
```

**2. 获取输出文件**
```python
# ✅ 获取所有输出文件，返回字典
# 格式: {"key1": ["s3://..."], "key2": ["s3://..."]}
# key 对应 manifest.json 中的 files.key
output_files = result.get_files()
if output_files:
    output_s3_url = output_files.get('output', [])[0]

# ✅ 获取所有输出文件的 URL 列表 (不关心 key)
# 格式: ["s3://...", "s3://..."]
all_file_urls = result.get_file_urls()
```

**完整示例 (推荐)**
```python
result = client.run(
    prefab_id="file-processing-prefab",
    version="0.1.5",
    function_name="parse_file",
    parameters={},
    files={"input": ["s3://bucket/document.pdf"]}
)

if result.is_success():
    # 1. 获取函数返回值 (业务数据)
    function_result = result.get_function_result()
    if function_result:
        if function_result.get('success'):
            print(f"消息: {function_result.get('message')}")
            print(f"内容: {function_result.get('content')}")
        else:
            print(f"业务错误: {function_result.get('error')}")

    # 2. 获取输出文件的 S3 URL
    output_files = result.get_files()
    if output_files and 'output' in output_files:
        output_s3_url = output_files['output'][0]
        print(f"输出文件 S3 URL: {output_s3_url}")
else:
    print(f"调用失败: {result.error}")
```

#### 响应层次说明

```
PrefabResult
├── status: CallStatus.SUCCESS                    # SDK 层状态（调用是否成功）
├── job_id: "933221b1-..."                       # 任务 ID
├── output                                        # Gateway 响应数据
│   ├── status: "SUCCESS"                        # Gateway 层状态
│   ├── output                                   # ← 预制件函数的返回值
│   │   ├── success: true                        #    （这里的字段由预制件定义）
│   │   ├── message: "..."                       #    （参考预制件的 manifest.returns）
│   │   └── ... 其他业务字段                      
│   └── files                                    # ← 输出文件列表
│       └── output: ["s3://..."]                 #    （key 对应 manifest.files.key）
└── error: null                                  # 错误信息（成功时为 null）
```

**关键理解**：
- `result.output['output']` 是**预制件函数的返回值**，对应 manifest. Json 中的 `returns` 定义
- `result.output['files']` 是**输出文件列表**，对应 manifest. Json 中的 `files` 定义
- 两个 `output` 是不同层次的概念（第一个是 Gateway 响应，第二个是函数返回值）

### BatchResult

```python
class BatchResult:
    job_id: str                  # 批量任务 ID
    status: str                  # 批量任务状态
    results: List[PrefabResult]  # 各个调用的结果列表
    
    def all_success() -> bool    # 判断是否全部成功
    def get_failed() -> List[PrefabResult]  # 获取失败的结果
```

### StreamEvent

```python
class StreamEvent:
    type: StreamEventType        # START / CONTENT / PROGRESS / DONE / ERROR
    data: Any                    # 事件数据
```

**StreamEventType 枚举值：**
- `START`: 流开始
- `CONTENT`: 内容片段
- `PROGRESS`: 进度更新
- `DONE`: 流结束
- `ERROR`: 错误

## 9. Agent 文件操作

**注意**：Agent 内部可以使用 SDK 进行文件操作，包括上传、下载、列出和清理文件。这些操作需要 Agent Context（通过 Gateway 调用时自动提供）。

### 上传永久文件

将处理结果保存为永久文件（存储在 `agent-outputs`）：

```python
# 上传本地文件到 S3
s3_url = client.upload_file(
    file_path="/tmp/result.txt",
    content_type="text/plain"
)
# 返回: "s3://bucket/agent-outputs/{user_id}/{agent_id}/{timestamp}-result.txt"
```

### 上传临时文件

上传临时工作文件（存储在 `agent-workspace`，支持 TTL）：

```python
# 上传临时文件，1小时后自动过期
s3_url = client.upload_temp_file(
    file_path="/tmp/temp_data.json",
    content_type="application/json",
    ttl_hours=1,
    session_id="task-123"  # 可选：关联到特定会话
)
# 返回: "s3://bucket/agent-workspace/{user_id}/{agent_id}/{session_id}/{timestamp}-temp_data.json"
```

### 下载文件

下载 S3 文件到本地：

```python
# 返回预签名下载 URL（有效期 1 小时）
download_url = client.download_file(
    s3_url="s3://bucket/path/to/file.pdf"
)

# 使用 httpx 下载文件
import httpx
response = httpx.get(download_url)
with open("/tmp/downloaded.pdf", "wb") as f:
    f.write(response.content)
```

### 列出文件

列出 Agent 的永久输出文件：

```python
# 列出所有输出文件
files = client.list_files()
# 返回: ["s3://bucket/agent-outputs/{user_id}/{agent_id}/file1.txt", ...]

# 列出特定前缀的文件
files = client.list_files(prefix="2025/11/07/")
```

### 列出临时文件

列出临时工作文件：

```python
# 列出所有临时文件
temp_files = client.list_temp_files()

# 列出特定会话的临时文件
temp_files = client.list_temp_files(session_id="task-123")
```

### 清理临时文件

删除临时文件（通常在任务完成后）：

```python
# 清理特定会话的所有临时文件
deleted_count = client.cleanup_temp_files(session_id="task-123")
print(f"已删除 {deleted_count} 个临时文件")

# 清理所有临时文件（谨慎使用）
deleted_count = client.cleanup_temp_files()
```

### 完整文件处理示例

```python
@app.post("/process-and-save")
async def process_and_save(
    request_data: Dict[str, Any],
    gateway_client: GatewayClient = Depends(get_gateway_client)
) -> Dict[str, Any]:
    """
    完整的文件处理流程：
    1. 接收输入文件 URL
    2. 下载并处理
    3. 上传临时文件
    4. 调用 Prefab 处理
    5. 上传最终结果
    6. 清理临时文件
    """
    try:
        # 1. 获取输入文件
        input_s3_url = request_data.get("parameters", {}).get("input_file")
        
        # 2. 下载输入文件
        download_url = gateway_client.download_file(input_s3_url)
        response = httpx.get(download_url)
        
        # 3. 处理文件并保存临时结果
        processed_data = process_file(response.content)
        with open("/tmp/temp_result.json", "w") as f:
            json.dump(processed_data, f)
        
        # 4. 上传临时文件
        temp_s3_url = gateway_client.upload_temp_file(
            file_path="/tmp/temp_result.json",
            content_type="application/json",
            ttl_hours=1,
            session_id=request_data.get("session_id", "default")
        )
        
        # 5. 调用 Prefab 进一步处理
        result = gateway_client.run(
            prefab_id="data-analyzer",
            version="1.0.0",
            function_name="analyze",
            parameters={},
            files={"input": [temp_s3_url]}
        )
        
        if result.is_success():
            # 6. 上传最终结果为永久文件
            final_output = result.get_function_result()
            with open("/tmp/final_result.txt", "w") as f:
                f.write(final_output.get("content", ""))
            
            final_s3_url = gateway_client.upload_file(
                file_path="/tmp/final_result.txt",
                content_type="text/plain"
            )
            
            # 7. 清理临时文件
            gateway_client.cleanup_temp_files(
                session_id=request_data.get("session_id", "default")
            )
            
            return {
                "success": True,
                "data": [{
                    "title": "处理完成",
                    "description": "文件已成功处理",
                    "metadata": {"output_file": final_s3_url},
                    "tags": ["已完成"]
                }],
                "message": "处理成功"
            }
        else:
            return {
                "success": False,
                "message": f"处理失败: {result.error}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "message": f"处理异常: {str(e)}"
        }
```

### 文件操作最佳实践

1. **使用临时文件**：中间过程使用 `upload_temp_file()`，最终结果使用 `upload_file()`
2. **设置合理的 TTL**：临时文件建议 1-24 小时，避免过长
3. **使用 session_id**：关联同一任务的临时文件，便于统一清理
4. **及时清理**：任务完成后调用 `cleanup_temp_files()` 释放存储空间
5. **错误处理**：文件操作可能失败（网络、权限等），务必添加异常处理

## 10. 高级用法

### 自定义超时

```python
client = GatewayClient(internal_token="...", timeout=120)
```

### 传递 S3 URL 给 Prefab

**说明**：调用 Prefab 时，文件参数使用 S3 URL：

```python
# 输入文件：传递 S3 URL
result = client.run(
    prefab_id="document-processor",
    version="1.0.0",
    function_name="extract_text",
    parameters={"language": "zh"},
    files={
        "input_docs": [
            "s3://bucket/document1.pdf",
            "s3://bucket/document2.pdf"
        ]
    }
)

# 输出文件：返回的也是 S3 URL
output_files = result.get_files()
# 示例: {"output_docs": ["s3://bucket/result.txt"]}
```

## 11. 示例代码

### 完整 Agent 示例（推荐）

```python
#!/usr/bin/env python3
"""
Agent 内部调用 Prefab 的完整示例

展示如何在 Agent 端点中正确使用 SDK 调用 Prefab
"""

from fastapi import FastAPI, Depends, Header
from gateway_sdk import GatewayClient
from typing import Dict, Any

app = FastAPI()

# 定义 Gateway Client 依赖注入
def get_gateway_client(
    x_internal_token: str = Header(..., alias="X-Internal-Token")
) -> GatewayClient:
    """
    从请求头获取 internal token 并创建 Gateway 客户端
    
    Gateway 会自动注入 X-Internal-Token 到 Agent 的请求头
    """
    return GatewayClient(internal_token=x_internal_token)


# ============================================
# 示例 1：Agent 端点调用 Prefab（推荐）
# ============================================

@app.post("/weather-advice")
async def get_weather_advice(
    request_data: Dict[str, Any],
    gateway_client: GatewayClient = Depends(get_gateway_client)
) -> Dict[str, Any]:
    """
    Agent 端点示例：调用天气 Prefab 获取建议
    
    接收用户请求 → 调用 Prefab → 返回结果
    """
    # 从请求参数中提取数据
    parameters = request_data.get("parameters", {})
    user_location = parameters.get("location")
    
    # 调用 Prefab
    result = gateway_client.run(
        prefab_id="weather-forecaster",
        version="1.0.0",
        function_name="get_forecast",
        parameters={"location": user_location}
    )
    
    # ✅ 第 1 步：检查 SDK 调用是否成功
    if result.is_success():
        # ✅ 第 2 步：获取函数返回值
        function_result = result.get_function_result()
        
        if function_result and function_result.get('success'):
            # 业务成功
            return {
                "success": True,
                "data": [{
                    "title": "天气预报",
                    "description": function_result.get('message'),
                    "status": "completed",
                    "metadata": function_result.get('data', {}),
                    "tags": ["已完成"]
                }],
                "message": "查询成功"
            }
        else:
            # 业务失败
            return {
                "success": False,
                "data": [{
                    "title": "查询失败",
                    "description": function_result.get('error', '未知错误'),
                    "status": "failed",
                    "tags": ["失败"]
                }],
                "message": "业务执行失败"
            }
    else:
        # SDK 调用失败
        return {
            "success": False,
            "data": [{
                "title": "调用失败",
                "description": str(result.error),
                "status": "failed",
                "tags": ["失败"]
            }],
            "message": "Prefab 调用失败"
        }


# ============================================
# 示例 2：调用涉及文件的 Prefab
# ============================================

@app.post("/process-document")
async def process_document(
    request_data: Dict[str, Any],
    gateway_client: GatewayClient = Depends(get_gateway_client)
) -> Dict[str, Any]:
    """
    Agent 端点示例：调用文档处理 Prefab
    
    处理流程：接收 S3 文件 URL → 调用 Prefab 处理 → 返回结果文件 URL
    """
    # 从请求参数中提取文件 URL
    parameters = request_data.get("parameters", {})
    input_file_url = parameters.get("document_url")  # S3 URL
    
    if not input_file_url:
        return {
            "success": False,
            "data": [],
            "message": "缺少必要参数: document_url"
        }
    
    # 调用文档处理 Prefab
    result = gateway_client.run(
        prefab_id="document-processor",
        version="1.0.0",
        function_name="extract_text",
        parameters={"language": "zh"},
        files={"input": [input_file_url]}  # 传递 S3 URL
    )
    
    if result.is_success():
        function_result = result.get_function_result()
        output_files = result.get_files()
        
        if function_result and function_result.get('success'):
            # 获取输出文件 S3 URL
            output_url = output_files.get('output', [])[0] if output_files.get('output') else None
            
            return {
                "success": True,
                "data": [{
                    "title": "文档处理完成",
                    "description": function_result.get('message'),
                    "status": "completed",
                    "metadata": {
                        "输出文件": output_url,
                        "提取字数": function_result.get('data', {}).get('word_count', 0)
                    },
                    "tags": ["已完成"]
                }],
                "message": "处理成功"
            }
        else:
            return {
                "success": False,
                "data": [],
                "message": function_result.get('error', '处理失败')
            }
    else:
        return {
            "success": False,
            "data": [],
            "message": f"Prefab 调用失败: {result.error}"
        }


# ============================================
# 示例 3：链式调用多个 Prefab
# ============================================

@app.post("/translate-and-analyze")
async def translate_and_analyze(
    request_data: Dict[str, Any],
    gateway_client: GatewayClient = Depends(get_gateway_client)
) -> Dict[str, Any]:
    """
    Agent 端点示例：链式调用多个 Prefab
    
    流程：翻译文本 → 分析情感 → 返回综合结果
    """
    parameters = request_data.get("parameters", {})
    text = parameters.get("text")
    
    if not text:
        return {"success": False, "message": "缺少文本参数"}
    
    try:
        # 第 1 步：翻译文本
        translate_result = gateway_client.run(
            prefab_id="translator",
            version="1.0.0",
            function_name="translate",
            parameters={"text": text, "target": "en"}
        )
        
        if not translate_result.is_success():
            return {"success": False, "message": "翻译失败"}
        
        translate_output = translate_result.get_function_result()
        if not translate_output or not translate_output.get('success'):
            return {"success": False, "message": "翻译失败"}
        
        translated_text = translate_output.get('translated_text')
        
        # 第 2 步：分析情感
        sentiment_result = gateway_client.run(
            prefab_id="sentiment-analyzer",
            version="1.0.0",
            function_name="analyze",
            parameters={"text": translated_text}
        )
        
        if not sentiment_result.is_success():
            return {"success": False, "message": "情感分析失败"}
        
        sentiment_output = sentiment_result.get_function_result()
        if not sentiment_output or not sentiment_output.get('success'):
            return {"success": False, "message": "情感分析失败"}
        
        # 返回综合结果
        return {
            "success": True,
            "data": [{
                "title": "分析完成",
                "description": "翻译和情感分析已完成",
                "status": "completed",
                "metadata": {
                    "原文": text,
                    "译文": translated_text,
                    "情感": sentiment_output.get('sentiment'),
                    "置信度": sentiment_output.get('confidence')
                },
                "tags": ["已完成"]
            }],
            "message": "处理成功"
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": [],
            "message": f"处理异常: {str(e)}"
        }


# 启动 Agent
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

```


## 12. 常见问题

**Q: 需要配置 Gateway 地址吗？**

A: **不需要**。SDK 有默认的 Gateway 地址（`http://agent-builder-gateway.default.svc.cluster.local`），Agent 内部调用时无需配置：
```python
# ✅ 推荐：无需配置 base_url
client = GatewayClient(internal_token=token)

# ❌ 不推荐：手动配置（除非特殊需求）
# client = GatewayClient(internal_token=token, base_url="...")
```

**Q: 如何处理超时？**

A: 设置 `timeout` 参数：
```python
def get_gateway_client(
    x_internal_token: str = Header(..., alias="X-Internal-Token")
) -> GatewayClient:
    return GatewayClient(internal_token=x_internal_token, timeout=120)
```

**Q: 如何停止流式响应？**

A: 使用 `break` 跳出循环：
```python
for event in client.run(..., stream=True):
    if some_condition:
        break
```

**Q: 批量调用部分失败如何处理？**

A: 检查每个结果：
```python
result = client.run_batch(calls)
for r in result.results:
    if r.is_success():
        function_result = r.get_function_result()
        print(function_result)
    else:
        print(r.error)
```

**Q: Agent 如何上传和下载文件？**

A: Agent 内部可以使用 SDK 的文件操作方法：
```python
# 上传文件
s3_url = client.upload_file("/tmp/result.txt", "text/plain")

# 下载文件
download_url = client.download_file("s3://bucket/path/file.pdf")
response = httpx.get(download_url)

# 上传临时文件（带 TTL）
temp_url = client.upload_temp_file("/tmp/temp.json", "application/json", ttl_hours=1)

# 清理临时文件
client.cleanup_temp_files(session_id="task-123")
```

**Q: 永久文件和临时文件有什么区别？**

A: 
- **永久文件** (`upload_file`): 存储在 `agent-outputs`，不会自动删除，用于最终输出
- **临时文件** (`upload_temp_file`): 存储在 `agent-workspace`，支持 TTL 自动过期，用于中间处理

建议：中间过程用临时文件，最终结果用永久文件

**Q: 如何处理大文件？**

A: 大文件处理建议：
- 使用 S 3 的分片上传功能（multipart upload）上传大文件
- 设置合适的 `timeout` 参数（如 300 秒）以适应大文件处理时间
- 考虑使用流式响应监控处理进度

**Q: 为什么响应有两层 `output`？**

A: 这是响应的嵌套结构，但**你通常不需要手动解析它**。
- 第一层 `result.output` 是 Gateway 的完整响应。
- 第二层 `result.output['output']` 是预制件函数的实际返回值。

**为避免手动解析，请使用便捷方法**：

```python
# ✅ 推荐：使用便捷方法
if result.is_success():
    # 直接获取函数返回值 (第二层 output)
    function_result = result.get_function_result()
    
    if function_result:
        success = function_result.get('success')
        message = function_result.get('message')

    # 直接获取输出文件
    files = result.get_files()
```