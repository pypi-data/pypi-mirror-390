"""
Core Module for BigConsole SDK.

This module provides core system operations including:
- Health check monitoring
- System information retrieval
- Version information
- Service status checks
"""

from typing import TYPE_CHECKING

from ..types.core import HealthCheckResponse, SystemInfo

if TYPE_CHECKING:
    from ..client.base_client import BaseGraphQLClient


class CoreModule:
    """
    Core Module for BigConsole SDK.

    Provides essential system operations for monitoring health,
    retrieving system information, and checking service status.
    """

    def __init__(self, client: "BaseGraphQLClient") -> None:
        """
        Initialize core module.

        Args:
            client: The GraphQL client instance for making requests.
        """
        self.client = client

    async def health_check(self) -> HealthCheckResponse:
        """
        Check BigConsole API health status.

        Performs a health check to verify that the BigConsole backend
        is operational and responsive. Returns status, timestamp, and version.

        Returns:
            HealthCheckResponse with status, timestamp, and version.

        Example:
            >>> health = await sdk.core.health_check()
            >>> print(f"Status: {health.status}")
            >>> print(f"Version: {health.version}")
            >>> print(f"Timestamp: {health.timestamp}")

        Raises:
            Exception: If the health check fails or service is unavailable.
        """
        query = """
        query HealthCheck {
            health {
                status
                timestamp
                version
            }
        }
        """

        response = await self.client.request(query)
        data = response["health"]

        return HealthCheckResponse(
            status=data["status"],
            timestamp=data.get("timestamp"),
            version=data.get("version"),
        )

    async def get_system_info(self) -> SystemInfo:
        """
        Get comprehensive system information.

        Retrieves detailed information about the BigConsole system including
        version, uptime, configuration, and operational metrics.

        Returns:
            SystemInfo with comprehensive system details.

        Example:
            >>> info = await sdk.core.get_system_info()
            >>> print(f"Version: {info.version}")
            >>> print(f"Environment: {info.environment}")
            >>> if info.uptime:
            ...     print(f"Uptime: {info.uptime} seconds")

        Note:
            This method may require appropriate permissions to access
            detailed system information.
        """
        query = """
        query SystemInfo {
            systemInfo {
                version
                environment
                uptime
                database
                features
            }
        }
        """

        response = await self.client.request(query)
        data = response["systemInfo"]

        return SystemInfo(
            version=data.get("version"),
            environment=data.get("environment"),
            uptime=data.get("uptime"),
            database=data.get("database"),
            features=data.get("features", []),
        )

    async def ping(self) -> bool:
        """
        Simple ping to check if the service is reachable.

        Performs a lightweight check to verify basic connectivity
        to the BigConsole backend.

        Returns:
            True if service is reachable, False otherwise.

        Example:
            >>> is_alive = await sdk.core.ping()
            >>> if is_alive:
            ...     print("Service is online")
            ... else:
            ...     print("Service is offline")
        """
        try:
            health = await self.health_check()
            return health.status == "ok" or health.status == "healthy"
        except Exception:
            return False

    async def get_version(self) -> str:
        """
        Get the BigConsole backend version.

        Retrieves just the version string of the currently running
        BigConsole backend service.

        Returns:
            Version string (e.g., "1.2.3").

        Example:
            >>> version = await sdk.core.get_version()
            >>> print(f"BigConsole Backend v{version}")
        """
        health = await self.health_check()
        return health.version or "unknown"

    async def check_service_status(self) -> dict:
        """
        Get detailed service status information.

        Performs comprehensive service checks and returns detailed
        status information including health, connectivity, and readiness.

        Returns:
            Dictionary containing service status details.

        Example:
            >>> status = await sdk.core.check_service_status()
            >>> print(f"Healthy: {status['healthy']}")
            >>> print(f"Version: {status['version']}")
            >>> print(f"Timestamp: {status['timestamp']}")
        """
        try:
            health = await self.health_check()
            return {
                "healthy": health.status in ["ok", "healthy"],
                "status": health.status,
                "version": health.version,
                "timestamp": health.timestamp,
                "reachable": True,
            }
        except Exception as e:
            return {
                "healthy": False,
                "status": "error",
                "version": None,
                "timestamp": None,
                "reachable": False,
                "error": str(e),
            }
