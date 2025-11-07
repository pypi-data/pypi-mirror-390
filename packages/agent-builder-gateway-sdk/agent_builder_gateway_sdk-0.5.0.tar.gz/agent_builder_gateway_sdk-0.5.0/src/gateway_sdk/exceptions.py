"""异常定义"""

from typing import Any, Dict, Optional


class GatewayError(Exception):
    """Gateway SDK 基础异常"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class AuthenticationError(GatewayError):
    """认证失败"""

    pass


class PrefabNotFoundError(GatewayError):
    """预制件不存在"""

    def __init__(self, prefab_id: str, version: str, message: Optional[str] = None):
        self.prefab_id = prefab_id
        self.version = version
        super().__init__(
            message or f"Prefab {prefab_id}@{version} not found",
            {"prefab_id": prefab_id, "version": version},
        )


class ValidationError(GatewayError):
    """参数验证失败"""

    pass


class QuotaExceededError(GatewayError):
    """配额超限"""

    def __init__(self, message: str, limit: int, used: int, quota_type: str):
        self.limit = limit
        self.used = used
        self.quota_type = quota_type
        super().__init__(
            message,
            {"limit": limit, "used": used, "quota_type": quota_type},
        )


class ServiceUnavailableError(GatewayError):
    """服务不可用"""

    pass


class MissingSecretError(GatewayError):
    """缺少必需的密钥"""

    def __init__(self, prefab_id: str, secret_name: str, instructions: Optional[str] = None):
        self.prefab_id = prefab_id
        self.secret_name = secret_name
        self.instructions = instructions
        message = f"Missing required secret '{secret_name}' for prefab '{prefab_id}'"
        if instructions:
            message += f"\n配置说明: {instructions}"
        super().__init__(
            message,
            {"prefab_id": prefab_id, "secret_name": secret_name, "instructions": instructions},
        )


class AgentContextRequiredError(GatewayError):
    """缺少 Agent 上下文（文件操作需要在 Agent 环境中运行）"""

    def __init__(self, message: Optional[str] = None):
        default_message = (
            "File operations require agent context.\n"
            "This feature is only available when running in production (called via Gateway Agent invoke).\n"
            "For third-party integrations, please use upload_input_file() to upload input files."
        )
        super().__init__(
            message or default_message,
            {"error_code": "MISSING_AGENT_CONTEXT"},
        )

