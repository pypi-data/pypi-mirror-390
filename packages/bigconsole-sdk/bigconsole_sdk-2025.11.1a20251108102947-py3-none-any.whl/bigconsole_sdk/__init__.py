from typing import Optional

from .ai import AIModule
from .auth import AuthModule
from .client.base_client import BaseGraphQLClient, BigconsoleSDKConfig
from .collaboration import CollaborationModule
from .core import CoreModule
from .dashboard import DashboardModule
from .data_source import DataSourceModule
from .types.common import *
from .user import UserModule
from .widget import WidgetModule

__version__ = "2025.11.1"


class BigconsoleSDK:
    def __init__(self, config: BigconsoleSDKConfig) -> None:
        self.client = BaseGraphQLClient(config)

        # Initialize all modules
        self.ai = AIModule(self.client)
        self.auth = AuthModule(self.client)
        self.collaboration = CollaborationModule(self.client)
        self.core = CoreModule(self.client)
        self.dashboard = DashboardModule(self.client)
        self.data_source = DataSourceModule(self.client)
        self.users = UserModule(self.client)
        self.widget = WidgetModule(self.client)

    def set_tokens(self, access_token: str, refresh_token: str) -> None:
        self.client.set_tokens(access_token=access_token, refresh_token=refresh_token)

    def clear_tokens(self) -> None:
        self.client.clear_tokens()

    def get_tokens(self) -> Optional[dict]:
        tokens = self.client.get_tokens()
        return (
            {"access_token": tokens.access_token, "refresh_token": tokens.refresh_token}
            if tokens
            else None
        )

    def set_endpoint(self, endpoint: str) -> None:
        self.client.set_endpoint(endpoint)

    def get_endpoint(self) -> str:
        return self.client.get_endpoint()


__all__ = [
    "BigconsoleSDK",
    "BigconsoleSDKConfig",
    "BaseGraphQLClient",
    "AIModule",
    "AuthModule",
    "CollaborationModule",
    "CoreModule",
    "DashboardModule",
    "DataSourceModule",
    "UserModule",
    "WidgetModule",
]
