"""Type definitions for Data Source module."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class DataSource:
    """Data source details."""

    id: str
    data_source_id: str
    name: str
    type: str
    config: Optional[Dict[str, Any]] = None
    cache_ttl: Optional[int] = None
    retry_policy: Optional[Dict[str, Any]] = None
    is_public: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


@dataclass
class DataSourceListResponse:
    """Response from listing data sources."""

    data_sources: List[DataSource]
    total: int
    skip: int
    limit: int


@dataclass
class CreateDataSourceInput:
    """Input for creating a data source."""

    data_source_id: str
    name: str
    type: str
    config: Dict[str, Any]
    cache_ttl: Optional[int] = None
    is_public: Optional[bool] = None


@dataclass
class CreateDataSourceResponse:
    """Response from creating a data source."""

    success: bool
    message: Optional[str] = None
    data_source: Optional[DataSource] = None


@dataclass
class UpdateDataSourceInput:
    """Input for updating a data source."""

    name: Optional[str] = None
    type: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    cache_ttl: Optional[int] = None


@dataclass
class UpdateDataSourceResponse:
    """Response from updating a data source."""

    success: bool
    message: Optional[str] = None
    data_source: Optional[DataSource] = None


@dataclass
class DeleteDataSourceResponse:
    """Response from deleting a data source."""

    success: bool
    message: Optional[str] = None


@dataclass
class TestDataSourceResponse:
    """Response from testing a data source."""

    success: bool
    message: Optional[str] = None
    data: Optional[Any] = None


@dataclass
class DataSourceData:
    """Data fetched from a data source."""

    success: bool
    data: Optional[Any] = None
    source: Optional[str] = None
    timestamp: Optional[str] = None
    error: Optional[str] = None
