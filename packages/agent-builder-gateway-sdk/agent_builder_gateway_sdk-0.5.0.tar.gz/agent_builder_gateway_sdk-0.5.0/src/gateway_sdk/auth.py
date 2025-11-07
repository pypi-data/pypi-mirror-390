"""认证管理"""

from typing import Optional


class AuthManager:
    """认证管理器"""

    def __init__(self, api_key: Optional[str] = None, jwt_token: Optional[str] = None):
        """
        初始化认证管理器

        Args:
            api_key: API Key（优先级高）
            jwt_token: JWT Token
        """
        self.api_key = api_key
        self.jwt_token = jwt_token

    def get_headers(self) -> dict[str, str]:
        """
        获取认证请求头

        Returns:
            认证请求头字典
        """
        headers: dict[str, str] = {}

        # API Key 优先
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        elif self.jwt_token:
            # 确保 Token 格式正确
            token = self.jwt_token
            if not token.startswith("Bearer "):
                token = f"Bearer {token}"
            headers["Authorization"] = token

        return headers

    def is_authenticated(self) -> bool:
        """
        判断是否已配置认证信息

        Returns:
            是否已配置认证
        """
        return bool(self.api_key or self.jwt_token)

