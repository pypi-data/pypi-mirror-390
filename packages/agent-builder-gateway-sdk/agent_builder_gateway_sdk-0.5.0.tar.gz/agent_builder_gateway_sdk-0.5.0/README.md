# Gateway SDK

Python SDK for Gateway - 用于调用预制件

## 概述

Gateway SDK 是一个用于调用预制件的 Python SDK。

### 核心特性

- ✅ 简洁的 API
- ✅ 支持 JWT Token 和 API Key 认证
- ✅ 流式响应支持（SSE）
- ✅ 完整的类型提示
- ✅ 完善的错误处理

## 安装

```bash
pip install agent-builder-gateway-sdk
```

## 快速开始

### 初始化客户端

```python
from gateway_sdk import GatewayClient

# 使用 JWT Token
client = GatewayClient(jwt_token="your-jwt-token")

# 或使用 API Key
client = GatewayClient(api_key="sk-xxx")

# 白名单模式（适用于 OpenHands 等白名单环境）
client = GatewayClient()  # 无需提供认证信息
```

**白名单模式说明**：
- 如果你的环境已配置白名单（如 OpenHands、内部开发环境），可以直接创建客户端而无需提供认证信息
- SDK 会以无鉴权模式发送请求，由 Gateway 基于 IP 白名单进行验证
- 这种模式简化了开发流程，无需管理 token

### 调用预制件

```python
result = client.run(
    prefab_id="llm-client",
    version="1.0.0",
    function_name="chat",
    parameters={"messages": [{"role": "user", "content": "Hello"}]}
)

if result.is_success():
    print(result.get_result())
else:
    print(f"Error: {result.error}")
```

### 链式调用

```python
llm = client.prefab("llm-client", "1.0.0")
result = llm.call("chat", messages=[...], model="gpt-4")
```

### 流式响应

```python
for event in client.run(..., stream=True):
    if event.type == "content":
        print(event.data, end="", flush=True)
    elif event.type == "done":
        print("\n完成")
```

### 批量调用

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
        print(r.get_result())
```

### 文件处理

**重要**: SDK 只接收 S3 URL，不负责文件上传/下载。

```python
# 传递 S3 URL 作为文件输入
result = client.run(
    prefab_id="video-processor",
    version="1.0.0",
    function_name="extract_audio",
    parameters={"format": "mp3"},
    files={"video": ["s3://bucket/input.mp4"]}
)

# 输出文件也是 S3 URL
output_files = result.get_files()
# {"audio": ["s3://bucket/output.mp3"]}
```

**文件处理流程**:
1. 📤 使用 S3 客户端上传文件，获取 S3 URL
2. 📝 将 S3 URL 传递给 SDK
3. 📥 从返回的 S3 URL 下载结果文件

---

## 🆕 Agent 文件操作（新特性）

**适用场景**: Agent 内部需要上传、下载、管理文件。

**核心特性**:
- ✅ 永久文件存储（agent-outputs）
- ✅ 临时文件支持（agent-workspace，自动删除）
- ✅ Session 管理（批量清理中间文件）
- ✅ 预签名 URL（直接下载）

### 初始化（Agent 专用）

```python
from gateway_sdk import GatewayClient
import os

# Agent 从请求头获取 internal_token
internal_token = os.environ.get("X_INTERNAL_TOKEN")

# 初始化客户端（internal_token 已包含 user_id 和 agent_id）
client = GatewayClient(internal_token=internal_token)
```

### 上传永久文件

```python
# 上传最终输出文件到 agent-outputs
result = client.upload_file("/tmp/result.pdf")

print(result["s3_url"])   # s3://bucket/agent-outputs/{user_id}/{agent_id}/...
print(result["filename"]) # result.pdf
print(result["size"])     # 文件大小（字节）
```

### 上传临时文件

```python
import uuid

# 创建 session ID（用于批量管理）
session_id = str(uuid.uuid4())

# 上传中间文件（默认 24 小时后自动删除）
result = client.upload_temp_file(
    "/tmp/intermediate.jpg",
    ttl=3600,         # 1 小时后删除
    session_id=session_id  # 关联到 session
)

print(result["s3_url"])  # s3://bucket/agent-workspace/{user_id}/{agent_id}/{session_id}/...
```

### 下载文件

```python
# 下载文件（支持所有 S3 URL）
client.download_file(
    "s3://bucket/agent-outputs/user123/agent456/result.pdf",
    "/tmp/downloaded_result.pdf"
)

# 或获取预签名 URL（推荐，适合大文件）
presigned_url = client.get_presigned_url(
    "s3://bucket/agent-outputs/...",
    expires_in=3600  # 1 小时有效期
)
# 可以直接用 presigned_url 下载
```

### 列出文件

```python
# 列出永久文件
result = client.list_files(limit=100)
for file in result["files"]:
    print(file["s3_url"], file["size"], file["last_modified"])

# 翻页
if "next_token" in result:
    next_page = client.list_files(limit=100, continuation_token=result["next_token"])
```

### 列出临时文件

```python
# 列出指定 session 的临时文件
result = client.list_temp_files(session_id=session_id)
for file in result["files"]:
    print(file["s3_url"])
```

### 清理临时文件

```python
# 任务完成后立即清理 session 的所有临时文件
deleted_count = client.cleanup_temp_files(session_id=session_id)
print(f"清理了 {deleted_count} 个临时文件")
```

### 完整工作流示例

```python
import uuid
from gateway_sdk import GatewayClient

# 1. 初始化
client = GatewayClient(internal_token=os.environ["X_INTERNAL_TOKEN"])

# 2. 创建 session
session_id = str(uuid.uuid4())

try:
    # 3. 下载输入文件（前端上传或其他 Agent 传入）
    client.download_file("s3://bucket/agent-inputs/.../input.mp4", "/tmp/input.mp4")
    
    # 4. 处理并上传中间文件（临时）
    # 假设提取音频
    extract_audio("/tmp/input.mp4", "/tmp/audio.wav")
    audio_result = client.upload_temp_file("/tmp/audio.wav", session_id=session_id)
    
    # 假设提取帧
    extract_frame("/tmp/input.mp4", "/tmp/frame.jpg")
    frame_result = client.upload_temp_file("/tmp/frame.jpg", session_id=session_id)
    
    # 5. 处理完成，上传最终结果（永久）
    process_video("/tmp/input.mp4", "/tmp/output.mp4")
    output_result = client.upload_file("/tmp/output.mp4")
    
    # 6. 清理临时文件
    client.cleanup_temp_files(session_id=session_id)
    
    # 7. 返回结果 S3 URL
    return {"output_url": output_result["s3_url"]}
    
except Exception as e:
    # 出错时也要清理临时文件
    client.cleanup_temp_files(session_id=session_id)
    raise
```

**最佳实践**:
1. 🗑️ 使用 `session_id` 管理临时文件，任务完成后立即清理
2. ⏰ 根据文件大小合理设置 `ttl`（避免浪费存储）
3. 📦 最终输出文件使用 `upload_file()`（永久存储）
4. 🔒 中间文件使用 `upload_temp_file()`（自动清理）

---

## 🌐 第三方集成（使用 API Key）

**适用场景**: 外部应用集成预制件生态（网站、脚本、CI/CD 等）

### 快速开始

```python
from gateway_sdk import GatewayClient

# 使用 API Key 初始化（自动转换为 internal_token）
client = GatewayClient.from_api_key("sk-xxx")

# 上传输入文件
s3_url = client.upload_input_file("/tmp/video.mp4", content_type="video/mp4")

# 调用 Prefab
result = client.run(
    prefab_id="video-processor",
    version="1.0.0",
    function_name="extract_audio",
    parameters={"format": "mp3"},
    files={"video": [s3_url]}
)

print(result.get_result())
```

### 完整示例

```python
from gateway_sdk import GatewayClient, AgentContextRequiredError

# 初始化
client = GatewayClient.from_api_key("sk-xxx")

try:
    # 1. 上传输入文件
    video_url = client.upload_input_file("/tmp/input.mp4", content_type="video/mp4")
    print(f"Uploaded: {video_url}")
    
    # 2. 调用 Prefab 处理
    result = client.run(
        prefab_id="video-processor",
        version="1.0.0",
        function_name="extract_audio",
        parameters={"format": "mp3"},
        files={"video": [video_url]}
    )
    
    # 3. 获取输出文件
    if result.is_success():
        output_files = result.get_files()
        print(f"Output: {output_files}")
    else:
        print(f"Error: {result.error}")

except AgentContextRequiredError as e:
    # 文件操作需要 Agent context（第三方集成不支持）
    print(f"不支持的操作: {e}")
    print("请使用 upload_input_file() 上传输入文件")
```

### 注意事项

**第三方集成的限制**：
- ✅ 可以调用任何 Prefab
- ✅ 可以上传输入文件（`upload_input_file()`）
- ❌ 不能使用 Agent 文件操作（`upload_file()`, `upload_temp_file()` 等）
  - 这些操作需要 Agent context，仅在生产环境（Agent invoke）中可用

**与 Agent 开发的区别**：

| 特性 | 第三方集成 | Agent 开发 |
|------|-----------|-----------|
| 初始化 | `from_api_key()` | `GatewayClient(internal_token)` |
| 调用 Prefab | ✅ 支持 | ✅ 支持 |
| 上传输入 | `upload_input_file()` | ✅ 任意上传 |
| Agent 文件操作 | ❌ 不支持 | ✅ 支持 |

---

## API 参考

### GatewayClient

#### 初始化

```python
GatewayClient(
    base_url: str = "http://nodeport.sensedeal.vip:30566",
    api_key: Optional[str] = None,
    jwt_token: Optional[str] = None,
    timeout: int = 60
)
```

**参数**：
- `api_key`: API Key
- `jwt_token`: JWT Token
- `timeout`: 请求超时时间（秒）

**注意**：必须提供 `api_key` 或 `jwt_token` 之一。

#### 方法

**run()** - 执行单个预制件

```python
run(
    prefab_id: str,
    version: str,
    function_name: str,
    parameters: Dict[str, Any],
    files: Optional[Dict[str, List[str]]] = None,  # 仅接受 S3 URL
    stream: bool = False
) -> Union[PrefabResult, Iterator[StreamEvent]]
```

参数:
- `files`: 文件输入，格式为 `{"参数名": ["s3://url1", "s3://url2"]}`，**仅接受 S3 URL**

**run_batch()** - 批量执行

```python
run_batch(calls: List[PrefabCall]) -> BatchResult
```

**prefab()** - 获取预制件对象

```python
prefab(prefab_id: str, version: str) -> Prefab
```

**list_prefabs()** - 列出预制件

```python
list_prefabs(status: Optional[str] = None) -> List[PrefabInfo]
```

**get_prefab_spec()** - 获取预制件规格

```python
get_prefab_spec(prefab_id: str, version: Optional[str] = None) -> Dict[str, Any]
```

### PrefabResult

预制件执行结果。

**属性**：
- `status`: 调用状态（SUCCESS / FAILED）
- `output`: 输出数据
- `error`: 错误信息
- `job_id`: 任务 ID

**方法**：
- `is_success()`: 判断是否成功
- `get(key, default)`: 获取输出字段
- `get_result()`: 获取业务结果
- `get_files()`: 获取输出文件

### StreamEvent

流式事件。

**属性**：
- `type`: 事件类型（start / content / progress / done / error）
- `data`: 事件数据

## 错误处理

```python
from gateway_sdk.exceptions import (
    GatewayError,
    AuthenticationError,
    PrefabNotFoundError,
    ValidationError,
    QuotaExceededError,
    ServiceUnavailableError,
    MissingSecretError,
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
except GatewayError as e:
    print(f"错误: {e}")
```

## 示例代码

- `examples/basic_usage.py` - 基础用法
- `examples/streaming.py` - 流式响应
- `examples/file_operations.py` - 文件操作（Agent 专用）

## 常见问题

**Q: 如何处理超时？**

A: 设置 `timeout` 参数：
```python
client = GatewayClient(jwt_token="...", timeout=120)
```

**Q: 如何调试？**

A: 启用日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Q: 如何停止流式响应？**

A: 使用 `break` 跳出循环：
```python
for event in client.run(..., stream=True):
    if some_condition:
        break
```

## 许可证

MIT License
