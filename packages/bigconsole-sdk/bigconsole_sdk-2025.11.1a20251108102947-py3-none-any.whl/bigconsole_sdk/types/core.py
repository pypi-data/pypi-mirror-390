"""Type definitions for Core module."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class HealthCheckResponse:
    """Health check response from the backend."""

    status: str
    timestamp: Optional[str] = None
    version: Optional[str] = None


@dataclass
class SystemInfo:
    """Comprehensive system information."""

    version: Optional[str] = None
    environment: Optional[str] = None
    uptime: Optional[int] = None
    database: Optional[Dict[str, Any]] = None
    features: List[str] = None
