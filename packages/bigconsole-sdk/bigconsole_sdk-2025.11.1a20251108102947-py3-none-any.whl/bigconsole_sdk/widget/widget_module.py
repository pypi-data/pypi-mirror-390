"""
Widget Module for BigConsole SDK.

This module provides comprehensive widget management including:
- Listing widgets with filtering and pagination
- Getting widget details
- Creating new widgets
- Updating existing widgets
- Deleting widgets
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..types.widget import (
    CreateWidgetInput,
    CreateWidgetResponse,
    DeleteWidgetResponse,
    UpdateWidgetInput,
    UpdateWidgetResponse,
    Widget,
    WidgetListResponse,
)

if TYPE_CHECKING:
    from ..client.base_client import BaseGraphQLClient


class WidgetModule:
    """
    Widget Module for BigConsole SDK.

    Provides complete CRUD operations for widget management including
    listing, creation, updates, and deletion.
    """

    def __init__(self, client: "BaseGraphQLClient") -> None:
        """
        Initialize widget module.

        Args:
            client: The GraphQL client instance for making requests.
        """
        self.client = client

    async def list(
        self,
        dashboard_id: Optional[str] = None,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> WidgetListResponse:
        """
        List all widgets with optional filtering.

        Retrieves a paginated list of widgets, optionally filtered by
        dashboard. Useful for displaying all widgets in a dashboard or
        managing widgets across the system.

        Args:
            dashboard_id: Optional dashboard ID to filter widgets by.
            skip: Number of widgets to skip for pagination.
            limit: Maximum number of widgets to return.

        Returns:
            WidgetListResponse with widgets, total count, and pagination info.

        Example:
            >>> # Get all widgets for a specific dashboard
            >>> result = await sdk.widget.list(
            ...     dashboard_id="sales-dashboard",
            ...     limit=50
            ... )
            >>> print(f"Found {result.total} widgets")
            >>> for widget in result.widgets:
            ...     print(f"- {widget.name} ({widget.type})")

            >>> # Get all widgets across all dashboards
            >>> all_widgets = await sdk.widget.list(limit=100)
        """
        query = """
        query ListWidgets($dashboardId: String, $skip: Int, $limit: Int) {
            widgets(dashboardId: $dashboardId, skip: $skip, limit: $limit) {
                widgets {
                    id
                    widgetId
                    dashboardId
                    dataSourceId
                    name
                    type
                    position
                    isActive
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
        if dashboard_id is not None:
            variables["dashboardId"] = dashboard_id
        if skip is not None:
            variables["skip"] = skip
        if limit is not None:
            variables["limit"] = limit

        response = await self.client.request(query, variables)
        data = response["widgets"]

        widgets = [
            Widget(
                id=widget["id"],
                widget_id=widget["widgetId"],
                dashboard_id=widget["dashboardId"],
                data_source_id=widget.get("dataSourceId"),
                name=widget["name"],
                type=widget["type"],
                config=None,  # Not included in list view
                position=widget.get("position"),
                is_active=widget.get("isActive", True),
                created_at=widget.get("createdAt"),
                updated_at=widget.get("updatedAt"),
            )
            for widget in data.get("widgets", [])
        ]

        return WidgetListResponse(
            widgets=widgets,
            total=data.get("total", 0),
            skip=data.get("skip", 0),
            limit=data.get("limit", 0),
        )

    async def get(self, widget_id: str) -> Widget:
        """
        Get widget details by ID.

        Retrieves complete widget information including configuration,
        position, data source binding, and settings.

        Args:
            widget_id: The unique identifier of the widget.

        Returns:
            Widget object with complete details including config.

        Example:
            >>> widget = await sdk.widget.get("sales-chart-widget")
            >>> print(f"Name: {widget.name}")
            >>> print(f"Type: {widget.type}")
            >>> print(f"Data Source: {widget.data_source_id}")
            >>> print(f"Config: {widget.config}")
        """
        query = """
        query GetWidget($widgetId: String!) {
            widget(widgetId: $widgetId) {
                id
                widgetId
                dashboardId
                dataSourceId
                name
                type
                config
                position
                isActive
                createdAt
                updatedAt
            }
        }
        """

        variables = {"widgetId": widget_id}
        response = await self.client.request(query, variables)
        data = response["widget"]

        return Widget(
            id=data["id"],
            widget_id=data["widgetId"],
            dashboard_id=data["dashboardId"],
            data_source_id=data.get("dataSourceId"),
            name=data["name"],
            type=data["type"],
            config=data.get("config"),
            position=data.get("position"),
            is_active=data.get("isActive", True),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt"),
        )

    async def create(self, input_data: CreateWidgetInput) -> CreateWidgetResponse:
        """
        Create a new widget.

        Creates a new widget with the specified type, configuration,
        data source binding, and position on the dashboard.

        Args:
            input_data: Widget creation input with required and optional fields.

        Returns:
            CreateWidgetResponse with success status and created widget.

        Example:
            >>> input_data = CreateWidgetInput(
            ...     widget_id="monthly-revenue-chart",
            ...     dashboard_id="sales-dashboard",
            ...     data_source_id="api-revenue-data",
            ...     name="Monthly Revenue",
            ...     type="line_chart",
            ...     config={
            ...         "xAxis": "month",
            ...         "yAxis": "revenue",
            ...         "color": "#3498db"
            ...     },
            ...     position={"x": 0, "y": 0, "w": 6, "h": 4}
            ... )
            >>> result = await sdk.widget.create(input_data)
            >>> if result.success:
            ...     print(f"Widget created: {result.widget.widget_id}")
        """
        mutation = """
        mutation CreateWidget($input: CreateWidgetInput!) {
            createWidget(input: $input) {
                success
                message
                widget {
                    id
                    widgetId
                    dashboardId
                    dataSourceId
                    name
                    type
                    createdAt
                }
            }
        }
        """

        variables = {
            "input": {
                "widgetId": input_data.widget_id,
                "dashboardId": input_data.dashboard_id,
                "name": input_data.name,
                "type": input_data.type,
                "config": input_data.config,
            }
        }

        if input_data.data_source_id is not None:
            variables["input"]["dataSourceId"] = input_data.data_source_id
        if input_data.position is not None:
            variables["input"]["position"] = input_data.position

        response = await self.client.request(mutation, variables)
        data = response["createWidget"]

        widget_data = data.get("widget", {})
        widget = Widget(
            id=widget_data.get("id", ""),
            widget_id=widget_data.get("widgetId", ""),
            dashboard_id=widget_data.get("dashboardId", ""),
            data_source_id=widget_data.get("dataSourceId"),
            name=widget_data.get("name", ""),
            type=widget_data.get("type", ""),
            config=None,
            position=None,
            is_active=True,
            created_at=widget_data.get("createdAt"),
            updated_at=None,
        )

        return CreateWidgetResponse(
            success=data["success"],
            message=data.get("message"),
            widget=widget,
        )

    async def update(self, widget_id: str, input_data: UpdateWidgetInput) -> UpdateWidgetResponse:
        """
        Update an existing widget.

        Updates widget properties including name, type, configuration,
        and position on the dashboard.

        Args:
            widget_id: The ID of the widget to update.
            input_data: Widget update input with fields to modify.

        Returns:
            UpdateWidgetResponse with success status and updated widget.

        Example:
            >>> input_data = UpdateWidgetInput(
            ...     name="Monthly Revenue (Updated)",
            ...     config={
            ...         "xAxis": "month",
            ...         "yAxis": "revenue",
            ...         "color": "#e74c3c",  # Changed color
            ...         "showGrid": True     # Added grid
            ...     },
            ...     position={"x": 0, "y": 0, "w": 8, "h": 5}  # Resized
            ... )
            >>> result = await sdk.widget.update("monthly-revenue-chart", input_data)
            >>> if result.success:
            ...     print(f"Widget updated: {result.widget.name}")
        """
        mutation = """
        mutation UpdateWidget($widgetId: String!, $input: UpdateWidgetInput!) {
            updateWidget(widgetId: $widgetId, input: $input) {
                success
                message
                widget {
                    id
                    widgetId
                    name
                    type
                    updatedAt
                }
            }
        }
        """

        variables: Dict[str, Any] = {"widgetId": widget_id, "input": {}}

        if input_data.name is not None:
            variables["input"]["name"] = input_data.name
        if input_data.type is not None:
            variables["input"]["type"] = input_data.type
        if input_data.config is not None:
            variables["input"]["config"] = input_data.config
        if input_data.position is not None:
            variables["input"]["position"] = input_data.position

        response = await self.client.request(mutation, variables)
        data = response["updateWidget"]

        widget_data = data.get("widget", {})
        widget = Widget(
            id=widget_data.get("id", ""),
            widget_id=widget_data.get("widgetId", ""),
            dashboard_id="",  # Not returned in update response
            data_source_id=None,
            name=widget_data.get("name", ""),
            type=widget_data.get("type", ""),
            config=None,
            position=None,
            is_active=True,
            created_at=None,
            updated_at=widget_data.get("updatedAt"),
        )

        return UpdateWidgetResponse(
            success=data["success"],
            message=data.get("message"),
            widget=widget,
        )

    async def delete(self, widget_id: str) -> DeleteWidgetResponse:
        """
        Delete a widget.

        Permanently removes a widget from its dashboard. This operation
        only affects the widget and does not delete the underlying data source.

        Args:
            widget_id: The ID of the widget to delete.

        Returns:
            DeleteWidgetResponse with success status and message.

        Example:
            >>> result = await sdk.widget.delete("old-widget-2023")
            >>> if result.success:
            ...     print("Widget deleted successfully")

        Warning:
            This operation is irreversible. The widget configuration and
            position will be permanently lost.
        """
        mutation = """
        mutation DeleteWidget($widgetId: String!) {
            deleteWidget(widgetId: $widgetId) {
                success
                message
            }
        }
        """

        variables = {"widgetId": widget_id}
        response = await self.client.request(mutation, variables)
        data = response["deleteWidget"]

        return DeleteWidgetResponse(
            success=data["success"],
            message=data.get("message"),
        )

    async def get_by_dashboard(self, dashboard_id: str) -> List[Widget]:
        """
        Get all widgets for a specific dashboard.

        Convenience method to retrieve all widgets belonging to a dashboard
        without pagination.

        Args:
            dashboard_id: The ID of the dashboard.

        Returns:
            List of Widget objects for the dashboard.

        Example:
            >>> widgets = await sdk.widget.get_by_dashboard("sales-dashboard")
            >>> for widget in widgets:
            ...     print(f"{widget.name} - Position: {widget.position}")
        """
        result = await self.list(dashboard_id=dashboard_id, limit=1000)
        return result.widgets

    async def bulk_update_positions(
        self, updates: List[Dict[str, Any]]
    ) -> List[UpdateWidgetResponse]:
        """
        Update positions for multiple widgets in a single operation.

        Efficiently updates the position of multiple widgets, useful for
        dashboard layout changes or drag-and-drop operations.

        Args:
            updates: List of dictionaries with widget_id and position.

        Returns:
            List of UpdateWidgetResponse for each update.

        Example:
            >>> updates = [
            ...     {"widget_id": "widget-1", "position": {"x": 0, "y": 0, "w": 6, "h": 4}},
            ...     {"widget_id": "widget-2", "position": {"x": 6, "y": 0, "w": 6, "h": 4}},
            ...     {"widget_id": "widget-3", "position": {"x": 0, "y": 4, "w": 12, "h": 3}}
            ... ]
            >>> results = await sdk.widget.bulk_update_positions(updates)
            >>> success_count = sum(1 for r in results if r.success)
            >>> print(f"Updated {success_count}/{len(updates)} widgets")
        """
        results = []
        for update in updates:
            widget_id = update["widget_id"]
            position = update["position"]
            input_data = UpdateWidgetInput(position=position)
            result = await self.update(widget_id, input_data)
            results.append(result)
        return results
