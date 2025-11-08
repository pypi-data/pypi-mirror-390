"""
Dashboard Module for BigConsole SDK.

This module provides comprehensive dashboard management including:
- Listing dashboards with filtering and pagination
- Getting dashboard details
- Creating new dashboards
- Updating existing dashboards
- Deleting dashboards
- Cloning dashboards with customization
"""

from typing import TYPE_CHECKING, Any, Dict, Optional

from ..types.dashboard import (
    CloneDashboardResponse,
    CreateDashboardInput,
    CreateDashboardResponse,
    Dashboard,
    DashboardListResponse,
    DeleteDashboardResponse,
    UpdateDashboardInput,
    UpdateDashboardResponse,
)

if TYPE_CHECKING:
    from ..client.base_client import BaseGraphQLClient


class DashboardModule:
    """
    Dashboard Module for BigConsole SDK.

    Provides complete CRUD operations for dashboard management including
    listing, creation, updates, deletion, and cloning.
    """

    def __init__(self, client: "BaseGraphQLClient") -> None:
        """
        Initialize dashboard module.

        Args:
            client: The GraphQL client instance for making requests.
        """
        self.client = client

    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        category: Optional[str] = None,
        is_public: Optional[bool] = None,
        metadata_only: Optional[bool] = None,
    ) -> DashboardListResponse:
        """
        List all dashboards with optional filtering.

        Retrieves a paginated list of dashboards with support for filtering
        by category, visibility, and metadata preferences.

        Args:
            skip: Number of dashboards to skip for pagination.
            limit: Maximum number of dashboards to return.
            category: Filter by dashboard category (e.g., "analytics", "monitoring").
            is_public: Filter by public/private status.
            metadata_only: If True, returns only metadata without full config.

        Returns:
            DashboardListResponse with dashboards, total count, and pagination info.

        Example:
            >>> # Get all public analytics dashboards
            >>> result = await sdk.dashboard.list(
            ...     category="analytics",
            ...     is_public=True,
            ...     limit=20
            ... )
            >>> print(f"Found {result.total} dashboards")
            >>> for dashboard in result.dashboards:
            ...     print(f"- {dashboard.name} ({dashboard.dashboard_id})")
        """
        query = """
        query ListDashboards(
            $skip: Int,
            $limit: Int,
            $category: String,
            $isPublic: Boolean,
            $metadataOnly: Boolean
        ) {
            dashboards(
                skip: $skip,
                limit: $limit,
                category: $category,
                isPublic: $isPublic,
                metadataOnly: $metadataOnly
            ) {
                dashboards {
                    id
                    dashboardId
                    name
                    description
                    category
                    icon
                    thumbnail
                    version
                    author
                    tags
                    isActive
                    isPublic
                    createdAt
                    updatedAt
                }
                total
                skip
                limit
            }
        }
        """

        variables: Dict[str, Any] = {}
        if skip is not None:
            variables["skip"] = skip
        if limit is not None:
            variables["limit"] = limit
        if category is not None:
            variables["category"] = category
        if is_public is not None:
            variables["isPublic"] = is_public
        if metadata_only is not None:
            variables["metadataOnly"] = metadata_only

        response = await self.client.request(query, variables)
        data = response["dashboards"]

        dashboards = [
            Dashboard(
                id=dashboard["id"],
                dashboard_id=dashboard["dashboardId"],
                name=dashboard["name"],
                description=dashboard.get("description"),
                category=dashboard.get("category"),
                icon=dashboard.get("icon"),
                thumbnail=dashboard.get("thumbnail"),
                version=dashboard.get("version"),
                author=dashboard.get("author"),
                tags=dashboard.get("tags", []),
                is_active=dashboard.get("isActive", True),
                is_public=dashboard.get("isPublic", False),
                config=None,  # Not included in list view
                created_at=dashboard.get("createdAt"),
                updated_at=dashboard.get("updatedAt"),
            )
            for dashboard in data.get("dashboards", [])
        ]

        return DashboardListResponse(
            dashboards=dashboards,
            total=data.get("total", 0),
            skip=data.get("skip", 0),
            limit=data.get("limit", 0),
        )

    async def get(self, dashboard_id: str) -> Dashboard:
        """
        Get dashboard details by ID.

        Retrieves complete dashboard information including configuration,
        metadata, and settings.

        Args:
            dashboard_id: The unique identifier of the dashboard.

        Returns:
            Dashboard object with complete details including config.

        Example:
            >>> dashboard = await sdk.dashboard.get("my-sales-dashboard")
            >>> print(f"Name: {dashboard.name}")
            >>> print(f"Category: {dashboard.category}")
            >>> print(f"Config: {dashboard.config}")
        """
        query = """
        query GetDashboard($dashboardId: String!) {
            dashboard(dashboardId: $dashboardId) {
                id
                dashboardId
                name
                description
                category
                icon
                thumbnail
                version
                author
                tags
                isActive
                isPublic
                config
                createdAt
                updatedAt
            }
        }
        """

        variables = {"dashboardId": dashboard_id}
        response = await self.client.request(query, variables)
        data = response["dashboard"]

        return Dashboard(
            id=data["id"],
            dashboard_id=data["dashboardId"],
            name=data["name"],
            description=data.get("description"),
            category=data.get("category"),
            icon=data.get("icon"),
            thumbnail=data.get("thumbnail"),
            version=data.get("version"),
            author=data.get("author"),
            tags=data.get("tags", []),
            is_active=data.get("isActive", True),
            is_public=data.get("isPublic", False),
            config=data.get("config"),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt"),
        )

    async def create(self, input_data: CreateDashboardInput) -> CreateDashboardResponse:
        """
        Create a new dashboard.

        Creates a new dashboard with the specified configuration, metadata,
        and settings.

        Args:
            input_data: Dashboard creation input with required and optional fields.

        Returns:
            CreateDashboardResponse with success status and created dashboard.

        Example:
            >>> input_data = CreateDashboardInput(
            ...     dashboard_id="sales-overview-2024",
            ...     name="Sales Overview 2024",
            ...     description="Comprehensive sales analytics dashboard",
            ...     category="analytics",
            ...     config={"layout": "grid", "columns": 12},
            ...     is_public=False
            ... )
            >>> result = await sdk.dashboard.create(input_data)
            >>> if result.success:
            ...     print(f"Dashboard created: {result.dashboard.dashboard_id}")
        """
        mutation = """
        mutation CreateDashboard($input: CreateDashboardInput!) {
            createDashboard(input: $input) {
                success
                message
                dashboard {
                    id
                    dashboardId
                    name
                    description
                    category
                    isPublic
                    isActive
                    createdAt
                }
            }
        }
        """

        variables = {
            "input": {
                "dashboardId": input_data.dashboard_id,
                "name": input_data.name,
                "config": input_data.config,
            }
        }

        if input_data.description is not None:
            variables["input"]["description"] = input_data.description
        if input_data.category is not None:
            variables["input"]["category"] = input_data.category
        if input_data.is_public is not None:
            variables["input"]["isPublic"] = input_data.is_public

        response = await self.client.request(mutation, variables)
        data = response["createDashboard"]

        dashboard_data = data.get("dashboard", {})
        dashboard = Dashboard(
            id=dashboard_data.get("id", ""),
            dashboard_id=dashboard_data.get("dashboardId", ""),
            name=dashboard_data.get("name", ""),
            description=dashboard_data.get("description"),
            category=dashboard_data.get("category"),
            icon=None,
            thumbnail=None,
            version=None,
            author=None,
            tags=[],
            is_active=dashboard_data.get("isActive", True),
            is_public=dashboard_data.get("isPublic", False),
            config=None,
            created_at=dashboard_data.get("createdAt"),
            updated_at=None,
        )

        return CreateDashboardResponse(
            success=data["success"],
            message=data.get("message"),
            dashboard=dashboard,
        )

    async def update(
        self, dashboard_id: str, input_data: UpdateDashboardInput
    ) -> UpdateDashboardResponse:
        """
        Update an existing dashboard.

        Updates dashboard properties including name, description, category,
        configuration, and visibility settings.

        Args:
            dashboard_id: The ID of the dashboard to update.
            input_data: Dashboard update input with fields to modify.

        Returns:
            UpdateDashboardResponse with success status and updated dashboard.

        Example:
            >>> input_data = UpdateDashboardInput(
            ...     name="Sales Overview 2024 - Q4",
            ...     description="Updated with Q4 metrics",
            ...     config={"layout": "grid", "columns": 16}
            ... )
            >>> result = await sdk.dashboard.update("sales-overview-2024", input_data)
            >>> if result.success:
            ...     print(f"Dashboard updated: {result.dashboard.name}")
        """
        mutation = """
        mutation UpdateDashboard($dashboardId: String!, $input: UpdateDashboardInput!) {
            updateDashboard(dashboardId: $dashboardId, input: $input) {
                success
                message
                dashboard {
                    id
                    dashboardId
                    name
                    description
                    category
                    isPublic
                    isActive
                    updatedAt
                }
            }
        }
        """

        variables: Dict[str, Any] = {"dashboardId": dashboard_id, "input": {}}

        if input_data.name is not None:
            variables["input"]["name"] = input_data.name
        if input_data.description is not None:
            variables["input"]["description"] = input_data.description
        if input_data.category is not None:
            variables["input"]["category"] = input_data.category
        if input_data.config is not None:
            variables["input"]["config"] = input_data.config
        if input_data.is_public is not None:
            variables["input"]["isPublic"] = input_data.is_public

        response = await self.client.request(mutation, variables)
        data = response["updateDashboard"]

        dashboard_data = data.get("dashboard", {})
        dashboard = Dashboard(
            id=dashboard_data.get("id", ""),
            dashboard_id=dashboard_data.get("dashboardId", ""),
            name=dashboard_data.get("name", ""),
            description=dashboard_data.get("description"),
            category=dashboard_data.get("category"),
            icon=None,
            thumbnail=None,
            version=None,
            author=None,
            tags=[],
            is_active=dashboard_data.get("isActive", True),
            is_public=dashboard_data.get("isPublic", False),
            config=None,
            created_at=None,
            updated_at=dashboard_data.get("updatedAt"),
        )

        return UpdateDashboardResponse(
            success=data["success"],
            message=data.get("message"),
            dashboard=dashboard,
        )

    async def delete(self, dashboard_id: str) -> DeleteDashboardResponse:
        """
        Delete a dashboard.

        Permanently removes a dashboard and all associated data.

        Args:
            dashboard_id: The ID of the dashboard to delete.

        Returns:
            DeleteDashboardResponse with success status and message.

        Example:
            >>> result = await sdk.dashboard.delete("old-dashboard-2023")
            >>> if result.success:
            ...     print("Dashboard deleted successfully")

        Warning:
            This operation is irreversible. Ensure you have backups or
            confirmation before deleting dashboards.
        """
        mutation = """
        mutation DeleteDashboard($dashboardId: String!) {
            deleteDashboard(dashboardId: $dashboardId) {
                success
                message
            }
        }
        """

        variables = {"dashboardId": dashboard_id}
        response = await self.client.request(mutation, variables)
        data = response["deleteDashboard"]

        return DeleteDashboardResponse(
            success=data["success"],
            message=data.get("message"),
        )

    async def clone(
        self, dashboard_id: str, new_dashboard_id: str, new_name: Optional[str] = None
    ) -> CloneDashboardResponse:
        """
        Clone an existing dashboard.

        Creates a complete copy of a dashboard with a new ID and optionally
        a new name. All widgets, configurations, and settings are duplicated.

        Args:
            dashboard_id: The ID of the dashboard to clone.
            new_dashboard_id: The ID for the new cloned dashboard.
            new_name: Optional new name for the cloned dashboard.

        Returns:
            CloneDashboardResponse with success status and cloned dashboard.

        Example:
            >>> result = await sdk.dashboard.clone(
            ...     "sales-overview-2024",
            ...     "sales-overview-2024-backup",
            ...     "Sales Overview 2024 - Backup",
            ... )
            >>> if result.success:
            ...     print(f"Dashboard cloned: {result.dashboard.dashboard_id}")

        Note:
            The cloned dashboard will have the same configuration as the
            original but can be modified independently afterwards.
        """
        mutation = """
        mutation CloneDashboard(
            $dashboardId: String!,
            $newDashboardId: String!,
            $newName: String
        ) {
            cloneDashboard(
                dashboardId: $dashboardId,
                newDashboardId: $newDashboardId,
                newName: $newName
            ) {
                success
                message
                dashboard {
                    id
                    dashboardId
                    name
                }
            }
        }
        """

        variables = {
            "dashboardId": dashboard_id,
            "newDashboardId": new_dashboard_id,
        }

        if new_name is not None:
            variables["newName"] = new_name

        response = await self.client.request(mutation, variables)
        data = response["cloneDashboard"]

        dashboard_data = data.get("dashboard", {})
        dashboard = Dashboard(
            id=dashboard_data.get("id", ""),
            dashboard_id=dashboard_data.get("dashboardId", ""),
            name=dashboard_data.get("name", ""),
            description=None,
            category=None,
            icon=None,
            thumbnail=None,
            version=None,
            author=None,
            tags=[],
            is_active=True,
            is_public=False,
            config=None,
            created_at=None,
            updated_at=None,
        )

        return CloneDashboardResponse(
            success=data["success"],
            message=data.get("message"),
            dashboard=dashboard,
        )
