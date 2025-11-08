"""Type definitions for Dashboard module."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Dashboard:
    """Dashboard details."""

    id: str
    dashboard_id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    icon: Optional[str] = None
    thumbnail: Optional[str] = None
    version: Optional[str] = None
    author: Optional[str] = None
    tags: List[str] = None
    is_active: bool = True
    is_public: bool = False
    config: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class DashboardListResponse:
    """Response from listing dashboards."""

    dashboards: List[Dashboard]
    total: int
    skip: int
    limit: int


@dataclass
class CreateDashboardInput:
    """Input for creating a dashboard."""

    dashboard_id: str
    name: str
    config: Dict[str, Any]
    description: Optional[str] = None
    category: Optional[str] = None
    is_public: Optional[bool] = None


@dataclass
class CreateDashboardResponse:
    """Response from creating a dashboard."""

    success: bool
    message: Optional[str] = None
    dashboard: Optional[Dashboard] = None


@dataclass
class UpdateDashboardInput:
    """Input for updating a dashboard."""

    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None


@dataclass
class UpdateDashboardResponse:
    """Response from updating a dashboard."""

    success: bool
    message: Optional[str] = None
    dashboard: Optional[Dashboard] = None


@dataclass
class DeleteDashboardResponse:
    """Response from deleting a dashboard."""

    success: bool
    message: Optional[str] = None


@dataclass
class CloneDashboardResponse:
    """Response from cloning a dashboard."""

    success: bool
    message: Optional[str] = None
    dashboard: Optional[Dashboard] = None
