"""
DevLake 配置管理

管理 DevLake API 连接配置，支持环境变量和配置文件。
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class DevLakeConfig:
    """DevLake 配置类"""

    # API 基础 URL
    base_url: str

    # API Token（如果需要认证）
    api_token: Optional[str] = None

    # 超时设置（秒）
    timeout: int = 30

    # 是否启用 SSL 验证
    verify_ssl: bool = True

    @classmethod
    def from_env(cls) -> "DevLakeConfig":
        """
        从环境变量加载配置

        环境变量：
        - DEVLAKE_BASE_URL: DevLake API 地址（默认：http://devlake.test.chinawayltd.com）
        - DEVLAKE_API_TOKEN: API Token（可选）
        - DEVLAKE_TIMEOUT: 请求超时时间（默认：30）
        - DEVLAKE_VERIFY_SSL: 是否验证 SSL（默认：true）

        Returns:
            DevLakeConfig: 配置实例
        """
        base_url = os.getenv("DEVLAKE_BASE_URL", "http://devlake.test.chinawayltd.com")
        api_token = os.getenv("DEVLAKE_API_TOKEN")
        timeout = int(os.getenv("DEVLAKE_TIMEOUT", "5"))
        verify_ssl = os.getenv("DEVLAKE_VERIFY_SSL", "true").lower() == "true"

        return cls(
            base_url=base_url.rstrip("/"),
            api_token=api_token,
            timeout=timeout,
            verify_ssl=verify_ssl
        )

    def get_headers(self) -> dict:
        """
        获取请求头

        Returns:
            dict: 请求头字典
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"

        return headers
