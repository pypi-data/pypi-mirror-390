"""
Agent Builder Gateway SDK
用于 AI 构建的程序调用预制件的 Python SDK
"""

from .client import GatewayClient
from .models import PrefabCall, PrefabResult, BatchResult, StreamEvent
from .exceptions import (
    GatewayError,
    AuthenticationError,
    PrefabNotFoundError,
    ValidationError,
    QuotaExceededError,
    ServiceUnavailableError,
    AgentContextRequiredError,
)

__version__ = "0.2.0"

__all__ = [
    "GatewayClient",
    "PrefabCall",
    "PrefabResult",
    "BatchResult",
    "StreamEvent",
    "GatewayError",
    "AuthenticationError",
    "PrefabNotFoundError",
    "ValidationError",
    "QuotaExceededError",
    "ServiceUnavailableError",
    "AgentContextRequiredError",
]

