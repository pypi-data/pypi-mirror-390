"""
DevLake API 客户端

提供与 DevLake REST API 交互的基础功能。
"""

import json
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from .config import DevLakeConfig


class DevLakeAPIError(Exception):
    """DevLake API 错误基类"""
    pass


class DevLakeConnectionError(DevLakeAPIError):
    """连接错误"""
    pass


class DevLakeNotFoundError(DevLakeAPIError):
    """资源不存在错误"""
    pass


class DevLakeValidationError(DevLakeAPIError):
    """验证错误"""
    pass


class DevLakeClient:
    """
    DevLake API 客户端

    提供与 DevLake REST API 交互的基础功能，包括：
    - GET/POST/PUT/PATCH/DELETE 请求
    - 错误处理和重试
    - 响应解析
    """

    def __init__(self, config: Optional[DevLakeConfig] = None):
        """
        初始化客户端

        Args:
            config: DevLake 配置，如果为 None 则从环境变量加载
        """
        self.config = config or DevLakeConfig.from_env()

    def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发起 HTTP 请求

        Args:
            method: HTTP 方法（GET, POST, PUT, PATCH, DELETE）
            path: API 路径（如 /api/connections）
            data: 请求体数据
            params: URL 查询参数

        Returns:
            Dict[str, Any]: 响应 JSON 数据

        Raises:
            DevLakeConnectionError: 连接失败
            DevLakeNotFoundError: 资源不存在
            DevLakeValidationError: 验证失败
            DevLakeAPIError: 其他 API 错误
        """
        # 构建完整 URL
        url = urljoin(self.config.base_url, path)

        # 添加查询参数
        if params:
            query_string = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query_string}"

        # 准备请求
        headers = self.config.get_headers()
        request_data = None

        if data is not None:
            request_data = json.dumps(data).encode("utf-8")
            headers["Content-Length"] = str(len(request_data))

        req = Request(url, data=request_data, headers=headers, method=method)

        try:
            with urlopen(req, timeout=self.config.timeout) as response:
                response_data = response.read().decode("utf-8")

                if not response_data:
                    return {}

                return json.loads(response_data)

        except HTTPError as e:
            error_body = e.read().decode("utf-8") if e.fp else ""

            if e.code == 404:
                raise DevLakeNotFoundError(f"Resource not found: {url}") from e
            elif e.code == 400:
                raise DevLakeValidationError(f"Validation error: {error_body}") from e
            else:
                raise DevLakeAPIError(
                    f"API error (status {e.code}): {error_body}"
                ) from e

        except URLError as e:
            raise DevLakeConnectionError(
                f"Connection error: {str(e)}"
            ) from e

        except json.JSONDecodeError as e:
            raise DevLakeAPIError(f"Invalid JSON response: {str(e)}") from e

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        发起 GET 请求

        Args:
            path: API 路径
            params: URL 查询参数

        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._make_request("GET", path, params=params)

    def post(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发起 POST 请求

        Args:
            path: API 路径
            data: 请求体数据

        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._make_request("POST", path, data=data)

    def put(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发起 PUT 请求

        Args:
            path: API 路径
            data: 请求体数据

        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._make_request("PUT", path, data=data)

    def patch(self, path: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发起 PATCH 请求

        Args:
            path: API 路径
            data: 请求体数据

        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._make_request("PATCH", path, data=data)

    def delete(self, path: str) -> Dict[str, Any]:
        """
        发起 DELETE 请求

        Args:
            path: API 路径

        Returns:
            Dict[str, Any]: 响应数据
        """
        return self._make_request("DELETE", path)

    def health_check(self) -> Dict[str, Any]:
        """
        健康检查

        Returns:
            Dict[str, Any]: 健康状态信息
        """
        try:
            # DevLake 的健康检查端点
            response = self.get("/api/ping")
            return {
                "status": "healthy",
                "message": "DevLake API is accessible",
                "base_url": self.config.base_url,
                "response": response
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": str(e),
                "base_url": self.config.base_url
            }
