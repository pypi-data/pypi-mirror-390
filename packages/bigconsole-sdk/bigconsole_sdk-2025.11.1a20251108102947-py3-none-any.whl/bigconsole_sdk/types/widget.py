"""Type definitions for Widget module."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class Widget:
    """Widget details."""

    id: str
    widget_id: str
    dashboard_id: str
    data_source_id: Optional[str]
    name: str
    type: str
    config: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class WidgetListResponse:
    """Response from listing widgets."""

    widgets: List[Widget]
    total: int
    skip: int
    limit: int


@dataclass
class CreateWidgetInput:
    """Input for creating a widget."""

    widget_id: str
    dashboard_id: str
    name: str
    type: str
    config: Dict[str, Any]
    data_source_id: Optional[str] = None
    position: Optional[Dict[str, Any]] = None


@dataclass
class CreateWidgetResponse:
    """Response from creating a widget."""

    success: bool
    message: Optional[str] = None
    widget: Optional[Widget] = None


@dataclass
class UpdateWidgetInput:
    """Input for updating a widget."""

    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    position: Optional[Dict[str, Any]] = None


@dataclass
class UpdateWidgetResponse:
    """Response from updating a widget."""

    success: bool
    message: Optional[str] = None
    widget: Optional[Widget] = None


@dataclass
class DeleteWidgetResponse:
    """Response from deleting a widget."""

    success: bool
    message: Optional[str] = None
