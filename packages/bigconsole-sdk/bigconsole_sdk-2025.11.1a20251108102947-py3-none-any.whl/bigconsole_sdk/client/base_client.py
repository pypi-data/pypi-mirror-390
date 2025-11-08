from dataclasses import dataclass
from typing import Any, Dict, Optional

import httpx


@dataclass
class BigconsoleSDKConfig:
    endpoint: str
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    timeout: float = 30.0


@dataclass
class AuthTokens:
    access_token: str
    refresh_token: str


class BaseGraphQLClient:
    def __init__(self, config: BigconsoleSDKConfig) -> None:
        self.config = config
        self.tokens: Optional[AuthTokens] = None

        if config.access_token and config.refresh_token:
            self.tokens = AuthTokens(
                access_token=config.access_token, refresh_token=config.refresh_token
            )

        self.client = httpx.AsyncClient(timeout=config.timeout, headers=self._get_headers())

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        if self.config.api_key:
            headers["X-API-Key"] = self.config.api_key

        if self.tokens and self.tokens.access_token:
            headers["Authorization"] = f"Bearer {self.tokens.access_token}"

        return headers

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        self.tokens = AuthTokens(access_token=access_token, refresh_token=refresh_token)
        self.client.headers.update(self._get_headers())

    def get_tokens(self) -> Optional[AuthTokens]:
        return self.tokens

    def clear_tokens(self) -> None:
        self.tokens = None
        # Remove authorization header
        if "Authorization" in self.client.headers:
            del self.client.headers["Authorization"]

    async def request(
        self, query: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        payload = {"query": query, "variables": variables or {}}

        try:
            response = await self.client.post(self.config.endpoint, json=payload)
            response.raise_for_status()

            data: Dict[str, Any] = await response.json()

            if "errors" in data:
                raise Exception(f"GraphQL Error: {data['errors']}")

            result: Dict[str, Any] = data.get("data", {})
            return result

        except httpx.HTTPStatusError as e:
            # Handle token refresh logic here if needed
            raise Exception(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Request Error: {str(e)}")

    def set_endpoint(self, endpoint: str) -> None:
        self.config.endpoint = endpoint
        # Update client with new endpoint by recreating it
        self.client = httpx.AsyncClient(timeout=self.config.timeout, headers=self._get_headers())

    def get_endpoint(self) -> str:
        return self.config.endpoint

    async def close(self) -> None:
        await self.client.aclose()

    async def __aenter__(self) -> "BaseGraphQLClient":
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.close()
