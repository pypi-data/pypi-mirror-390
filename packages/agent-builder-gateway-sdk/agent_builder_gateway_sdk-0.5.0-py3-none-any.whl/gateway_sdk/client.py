"""Gateway 客户端（内部版本）

用于 Agent/Prefab 内部调用网关

架构说明：
- Agent 从请求头获取 X-Internal-Token（由网关传入）
- Prefab 从请求头获取 X-Internal-Token（由 Agent 传入）
- SDK 直接传递 internal token，不做任何转换
"""

import httpx
from typing import Any, Dict, List, Optional, Union, Iterator
from .models import PrefabCall, PrefabResult, BatchResult, CallStatus, StreamEvent
from .streaming import parse_sse_stream
from .exceptions import (
    GatewayError,
    AuthenticationError,
    PrefabNotFoundError,
    ValidationError,
    QuotaExceededError,
    ServiceUnavailableError,
    MissingSecretError,
)


# Gateway 地址
DEFAULT_GATEWAY_URL = "http://agent-builder-gateway-test.sensedeal.vip"


class GatewayClient:
    """Gateway SDK 主客户端（内部版本）"""

    def __init__(
        self,
        internal_token: str,
        base_url: str = DEFAULT_GATEWAY_URL,
        timeout: int = 60,
    ):
        """
        初始化客户端

        Args:
            internal_token: 内部 token（从请求头 X-Internal-Token 获取）
            base_url: Gateway 地址（默认使用测试环境）
            timeout: 请求超时时间（秒）
        
        Note:
            此 SDK 专门用于 Agent/Prefab 内部调用，不支持外部 API Key/JWT。
            外部用户请使用外部端点 /v1/external/invoke_*
        """
        if not internal_token:
            raise ValueError("internal_token is required for Gateway SDK")
        
        self.base_url = base_url.rstrip("/")
        self.internal_token = internal_token
        self.timeout = timeout

    @classmethod
    def from_api_key(cls, api_key: str, base_url: str = DEFAULT_GATEWAY_URL, timeout: int = 60):
        """
        从 API Key 创建客户端（第三方集成使用）

        Args:
            api_key: API Key（sk-xxx）
            base_url: Gateway 地址
            timeout: 请求超时时间（秒）

        Returns:
            GatewayClient 实例

        Raises:
            AuthenticationError: API Key 无效
            ServiceUnavailableError: 网络请求失败

        Example:
            ```python
            # 第三方集成
            client = GatewayClient.from_api_key("sk-xxx")
            
            # 上传输入文件
            s3_url = client.upload_input_file("/tmp/video.mp4")
            
            # 调用 Prefab
            result = client.run("video-processor", "1.0.0", "extract_audio", files={"video": [s3_url]})
            ```
        """
        from .exceptions import AuthenticationError, ServiceUnavailableError
        
        url = f"{base_url.rstrip('/')}/v1/auth/convert_to_internal_token"
        headers = {"Authorization": f"Bearer {api_key}"}
        
        try:
            with httpx.Client(timeout=timeout) as http_client:
                response = http_client.post(url, headers=headers)
                
                if response.status_code == 401:
                    raise AuthenticationError("Invalid or expired API Key")
                
                response.raise_for_status()
                data = response.json()
                internal_token = data["internal_token"]
                
                return cls(internal_token=internal_token, base_url=base_url, timeout=timeout)
        
        except httpx.TimeoutException:
            raise ServiceUnavailableError("请求超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"网络请求失败: {str(e)}")

    def run(
        self,
        prefab_id: str,
        version: str,
        function_name: str,
        parameters: Dict[str, Any],
        files: Optional[Dict[str, List[str]]] = None,
        stream: bool = False,
    ) -> Union[PrefabResult, Iterator[StreamEvent]]:
        """
        执行单个预制件

        Args:
            prefab_id: 预制件 ID
            version: 版本号
            function_name: 函数名
            parameters: 参数字典
            files: 文件输入（可选）
            stream: 是否流式返回

        Returns:
            PrefabResult 或 StreamEvent 迭代器

        Raises:
            AuthenticationError: 认证失败
            PrefabNotFoundError: 预制件不存在
            ValidationError: 参数验证失败
            QuotaExceededError: 配额超限
            ServiceUnavailableError: 服务不可用
            MissingSecretError: 缺少必需的密钥
        """
        call = PrefabCall(
            prefab_id=prefab_id,
            version=version,
            function_name=function_name,
            parameters=parameters,
            files=files,
        )

        if stream:
            return self._run_streaming(call)
        else:
            result = self.run_batch([call])
            return result.results[0]

    def run_batch(self, calls: List[PrefabCall]) -> BatchResult:
        """
        批量执行预制件

        Args:
            calls: 预制件调用列表

        Returns:
            BatchResult

        Raises:
            同 run() 方法
        """
        url = f"{self.base_url}/v1/internal/run"
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Token": self.internal_token
        }

        payload = {"calls": [call.to_dict() for call in calls]}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                self._handle_error_response(response)

                data = response.json()
                results = [
                    PrefabResult(
                        status=CallStatus(r["status"]),
                        output=r.get("output"),
                        error=r.get("error"),
                        job_id=data.get("job_id"),
                    )
                    for r in data["results"]
                ]

                return BatchResult(job_id=data["job_id"], status=data["status"], results=results)

        except httpx.TimeoutException:
            raise ServiceUnavailableError("请求超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"网络请求失败: {str(e)}")

    def _run_streaming(self, call: PrefabCall) -> Iterator[StreamEvent]:
        """
        流式执行预制件

        Args:
            call: 预制件调用

        Yields:
            StreamEvent
        """
        url = f"{self.base_url}/v1/internal/run"
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Token": self.internal_token
        }

        payload = {"calls": [call.to_dict()]}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream("POST", url, json=payload, headers=headers) as response:
                    self._handle_error_response(response)

                    # 解析 SSE 流
                    yield from parse_sse_stream(response.iter_bytes())

        except httpx.TimeoutException:
            raise ServiceUnavailableError("请求超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"网络请求失败: {str(e)}")

    def _handle_error_response(self, response: httpx.Response) -> None:
        """
        处理错误响应

        Args:
            response: HTTP 响应

        Raises:
            对应的异常
        """
        if response.status_code < 400:
            return

        try:
            error_data = response.json()
            detail = error_data.get("detail", "Unknown error")

            # 解析错误详情
            if isinstance(detail, dict):
                error_code = detail.get("error_code", "UNKNOWN_ERROR")
                message = detail.get("message", str(detail))
            else:
                error_code = "UNKNOWN_ERROR"
                message = str(detail)

        except Exception:
            error_code = "UNKNOWN_ERROR"
            # 对于流式响应，需要先读取内容
            try:
                error_text = response.text
            except Exception:
                # 如果无法读取，先读取响应再获取文本
                try:
                    response.read()
                    error_text = response.text
                except Exception:
                    error_text = "Unable to read error response"
            message = f"HTTP {response.status_code}: {error_text}"

        # 根据状态码和错误码抛出对应异常
        if response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError(message)
        elif response.status_code == 404:
            raise PrefabNotFoundError("unknown", "unknown", message)
        elif response.status_code == 422:
            raise ValidationError(message)
        elif response.status_code == 429:
            # 配额超限
            if isinstance(detail, dict):
                raise QuotaExceededError(
                    message,
                    limit=detail.get("limit", 0),
                    used=detail.get("used", 0),
                    quota_type=detail.get("quota_type", "unknown"),
                )
            else:
                raise QuotaExceededError(message, 0, 0, "unknown")
        elif response.status_code == 400 and error_code == "MISSING_SECRET":
            # 缺少密钥
            if isinstance(detail, dict):
                raise MissingSecretError(
                    prefab_id=detail.get("prefab_id", "unknown"),
                    secret_name=detail.get("secret_name", "unknown"),
                    instructions=detail.get("instructions"),
                )
            else:
                raise MissingSecretError("unknown", "unknown")
        elif response.status_code == 400 and error_code == "MISSING_AGENT_CONTEXT":
            # 缺少 Agent 上下文（文件操作需要）
            from .exceptions import AgentContextRequiredError
            raise AgentContextRequiredError(message)
        elif response.status_code >= 500:
            raise ServiceUnavailableError(message)
        else:
            raise GatewayError(message, {"error_code": error_code})

    # ========== 文件操作 API（新增）==========

    def upload_input_file(self, file_path: str, content_type: Optional[str] = None) -> str:
        """
        上传输入文件（第三方集成使用）

        Args:
            file_path: 本地文件路径
            content_type: 内容类型（可选，如 "video/mp4"）

        Returns:
            s3_url: S3 文件地址，可用于调用 Prefab

        Raises:
            GatewayError: 上传失败
            AgentContextRequiredError: 不会抛出（此方法不需要 agent context）

        Example:
            ```python
            client = GatewayClient.from_api_key("sk-xxx")
            
            # 上传输入文件
            s3_url = client.upload_input_file("/tmp/video.mp4", content_type="video/mp4")
            
            # 调用 Prefab
            result = client.run(
                "video-processor", 
                "1.0.0", 
                "extract_audio",
                files={"video": [s3_url]}
            )
            ```
        """
        import os
        from pathlib import Path

        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        filename = Path(file_path).name
        
        # 1. 获取预签名上传 URL
        url = f"{self.base_url}/internal/files/generate_upload_url"
        headers = {
            "Content-Type": "application/json",
            "X-Internal-Token": self.internal_token
        }
        payload = {
            "filename": filename,
            "content_type": content_type
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload, headers=headers)
                self._handle_error_response(response)
                
                data = response.json()
                upload_url = data["upload_url"]
                s3_url = data["s3_url"]
            
            # 2. 使用预签名 URL 上传到 S3
            with open(file_path, "rb") as f:
                file_data = f.read()
            
            upload_headers = {}
            if content_type:
                upload_headers["Content-Type"] = content_type
            
            with httpx.Client(timeout=self.timeout * 2) as client:  # 上传超时时间加倍
                upload_response = client.put(upload_url, content=file_data, headers=upload_headers)
                upload_response.raise_for_status()
            
            return s3_url

        except httpx.TimeoutException:
            raise ServiceUnavailableError("上传超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"上传失败: {str(e)}")

    def upload_file(self, file_path: str) -> Dict[str, Any]:
        """
        上传永久文件到 agent-outputs

        Args:
            file_path: 本地文件路径

        Returns:
            {
                "success": bool,
                "s3_url": str,  # S3 地址
                "filename": str,
                "size": int
            }

        Raises:
            GatewayError: 上传失败

        Example:
            result = client.upload_file("/tmp/result.pdf")
            s3_url = result["s3_url"]  # s3://bucket/agent-outputs/{user_id}/{agent_id}/...
        """
        import os

        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        url = f"{self.base_url}/internal/files/upload"
        headers = {"X-Internal-Token": self.internal_token}

        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(url, files=files, headers=headers)
                    self._handle_error_response(response)
                    return response.json()

        except httpx.TimeoutException:
            raise ServiceUnavailableError("上传超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"上传失败: {str(e)}")

    def upload_temp_file(
        self,
        file_path: str,
        ttl: int = 86400,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        上传临时文件到 agent-workspace（带 TTL）

        Args:
            file_path: 本地文件路径
            ttl: 生存时间（秒），默认 86400（24 小时）
            session_id: 会话 ID（可选），用于批量管理

        Returns:
            {
                "success": bool,
                "s3_url": str,
                "filename": str,
                "size": int
            }

        Raises:
            GatewayError: 上传失败

        Example:
            # 默认 24 小时后删除
            result = client.upload_temp_file("/tmp/intermediate.jpg")

            # 1 小时后删除
            result = client.upload_temp_file("/tmp/temp.dat", ttl=3600)

            # 关联到 session
            session_id = str(uuid.uuid4())
            result = client.upload_temp_file("/tmp/temp.jpg", session_id=session_id)
        """
        import os

        if not os.path.exists(file_path):
            raise ValueError(f"File not found: {file_path}")

        url = f"{self.base_url}/internal/files/upload_temp"
        headers = {"X-Internal-Token": self.internal_token}

        try:
            with open(file_path, "rb") as f:
                files = {"file": (os.path.basename(file_path), f)}
                data = {"ttl": ttl}
                if session_id:
                    data["session_id"] = session_id

                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(url, files=files, data=data, headers=headers)
                    self._handle_error_response(response)
                    return response.json()

        except httpx.TimeoutException:
            raise ServiceUnavailableError("上传超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"上传失败: {str(e)}")

    def download_file(
        self,
        s3_url: str,
        local_path: str,
        mode: str = "presigned"
    ) -> None:
        """
        下载文件

        Args:
            s3_url: S3 文件 URL
            local_path: 本地保存路径
            mode: 下载模式（"presigned" 推荐，"stream" 暂不支持）

        Raises:
            GatewayError: 下载失败

        Example:
            client.download_file("s3://bucket/agent-outputs/...", "/tmp/result.pdf")
        """
        import os

        if mode != "presigned":
            raise ValueError("目前仅支持 presigned 模式")

        # 获取预签名 URL
        presigned_url = self.get_presigned_url(s3_url)

        try:
            # 直接从 S3 下载
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(presigned_url)
                response.raise_for_status()

                # 保存到本地
                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, "wb") as f:
                    f.write(response.content)

        except httpx.TimeoutException:
            raise ServiceUnavailableError("下载超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"下载失败: {str(e)}")

    def get_presigned_url(
        self,
        s3_url: str,
        expires_in: int = 3600
    ) -> str:
        """
        获取预签名 URL（用于直接下载）

        Args:
            s3_url: S3 文件 URL
            expires_in: 有效期（秒），默认 3600（1 小时）

        Returns:
            预签名 URL（HTTPS）

        Raises:
            GatewayError: 获取失败

        Example:
            url = client.get_presigned_url("s3://bucket/agent-outputs/...")
            # 可以直接用浏览器访问这个 URL 下载文件
        """
        url = f"{self.base_url}/internal/files/download"
        headers = {"X-Internal-Token": self.internal_token}
        params = {
            "s3_url": s3_url,
            "mode": "presigned",
            "expires_in": expires_in
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params, headers=headers)
                self._handle_error_response(response)
                data = response.json()
                return data["presigned_url"]

        except httpx.TimeoutException:
            raise ServiceUnavailableError("请求超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"请求失败: {str(e)}")

    def list_files(
        self,
        limit: int = 100,
        continuation_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        列出永久文件（agent-outputs）

        Args:
            limit: 最大返回数量，默认 100
            continuation_token: 分页 token（可选）

        Returns:
            {
                "files": [
                    {
                        "key": str,
                        "size": int,
                        "last_modified": str,
                        "s3_url": str
                    }
                ],
                "next_token": str (optional)
            }

        Raises:
            GatewayError: 获取失败

        Example:
            result = client.list_files(limit=50)
            for file in result["files"]:
                print(file["s3_url"])

            # 翻页
            if "next_token" in result:
                next_page = client.list_files(limit=50, continuation_token=result["next_token"])
        """
        url = f"{self.base_url}/internal/files/list"
        headers = {"X-Internal-Token": self.internal_token}
        params = {"limit": limit}
        if continuation_token:
            params["continuation_token"] = continuation_token

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params, headers=headers)
                self._handle_error_response(response)
                return response.json()

        except httpx.TimeoutException:
            raise ServiceUnavailableError("请求超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"请求失败: {str(e)}")

    def list_temp_files(
        self,
        session_id: Optional[str] = None,
        limit: int = 100,
        continuation_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        列出临时文件（agent-workspace）

        Args:
            session_id: 会话 ID（可选），不指定则列出所有临时文件
            limit: 最大返回数量，默认 100
            continuation_token: 分页 token（可选）

        Returns:
            同 list_files()

        Raises:
            GatewayError: 获取失败

        Example:
            # 列出所有临时文件
            result = client.list_temp_files()

            # 列出指定 session 的临时文件
            result = client.list_temp_files(session_id="abc123")
        """
        url = f"{self.base_url}/internal/files/list_temp"
        headers = {"X-Internal-Token": self.internal_token}
        params = {"limit": limit}
        if session_id:
            params["session_id"] = session_id
        if continuation_token:
            params["continuation_token"] = continuation_token

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(url, params=params, headers=headers)
                self._handle_error_response(response)
                return response.json()

        except httpx.TimeoutException:
            raise ServiceUnavailableError("请求超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"请求失败: {str(e)}")

    def cleanup_temp_files(self, session_id: str) -> int:
        """
        立即清理指定 session 的所有临时文件

        Args:
            session_id: 会话 ID

        Returns:
            删除的文件数量

        Raises:
            GatewayError: 清理失败

        Example:
            # Agent 任务完成后立即清理
            count = client.cleanup_temp_files(session_id="abc123")
            print(f"Cleaned up {count} temporary files")
        """
        url = f"{self.base_url}/internal/files/cleanup_temp"
        headers = {"X-Internal-Token": self.internal_token}
        params = {"session_id": session_id}

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.delete(url, params=params, headers=headers)
                self._handle_error_response(response)
                data = response.json()
                return data["deleted_count"]

        except httpx.TimeoutException:
            raise ServiceUnavailableError("请求超时")
        except httpx.RequestError as e:
            raise ServiceUnavailableError(f"请求失败: {str(e)}")

