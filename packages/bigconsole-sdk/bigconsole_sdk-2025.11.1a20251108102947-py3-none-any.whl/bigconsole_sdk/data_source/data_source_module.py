"""
Data Source Module for BigConsole SDK.

This module provides comprehensive data source management including:
- Listing data sources with filtering and pagination
- Getting data source details
- Creating new data sources
- Updating existing data sources
- Deleting data sources
- Testing data source connections
- Fetching data from data sources
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..types.data_source import (
    CreateDataSourceInput,
    CreateDataSourceResponse,
    DataSource,
    DataSourceData,
    DataSourceListResponse,
    DeleteDataSourceResponse,
    TestDataSourceResponse,
    UpdateDataSourceInput,
    UpdateDataSourceResponse,
)

if TYPE_CHECKING:
    from ..client.base_client import BaseGraphQLClient


class DataSourceModule:
    """
    Data Source Module for BigConsole SDK.

    Provides complete CRUD operations for data source management including
    listing, creation, updates, deletion, testing, and data fetching.
    """

    def __init__(self, client: "BaseGraphQLClient") -> None:
        """
        Initialize data source module.

        Args:
            client: The GraphQL client instance for making requests.
        """
        self.client = client

    async def list(
        self,
        skip: Optional[int] = None,
        limit: Optional[int] = None,
        type: Optional[str] = None,
        is_public: Optional[bool] = None,
        console: Optional[str] = None,
    ) -> DataSourceListResponse:
        """
        List all data sources with optional filtering.

        Retrieves a paginated list of data sources with support for filtering
        by type, visibility, and console assignment.

        Args:
            skip: Number of data sources to skip for pagination.
            limit: Maximum number of data sources to return.
            type: Filter by data source type (e.g., "rest", "graphql", "database").
            is_public: Filter by public/private status.
            console: Filter by console identifier.

        Returns:
            DataSourceListResponse with data sources, total count, and pagination info.

        Example:
            >>> # Get all REST API data sources
            >>> result = await sdk.data_source.list(
            ...     type="rest",
            ...     limit=20
            ... )
            >>> print(f"Found {result.total} data sources")
            >>> for ds in result.data_sources:
            ...     print(f"- {ds.name} ({ds.type})")
        """
        query = """
        query ListDataSources(
            $skip: Int,
            $limit: Int,
            $type: String,
            $isPublic: Boolean,
            $console: String
        ) {
            dataSources(
                skip: $skip,
                limit: $limit,
                type: $type,
                isPublic: $isPublic,
                console: $console
            ) {
                dataSources {
                    id
                    dataSourceId
                    name
                    type
                    cacheTtl
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
        if type is not None:
            variables["type"] = type
        if is_public is not None:
            variables["isPublic"] = is_public
        if console is not None:
            variables["console"] = console

        response = await self.client.request(query, variables)
        data = response["dataSources"]

        data_sources = [
            DataSource(
                id=ds["id"],
                data_source_id=ds["dataSourceId"],
                name=ds["name"],
                type=ds["type"],
                config=None,  # Not included in list view
                cache_ttl=ds.get("cacheTtl"),
                retry_policy=None,
                is_public=ds.get("isPublic", False),
                created_at=ds.get("createdAt"),
                updated_at=ds.get("updatedAt"),
            )
            for ds in data.get("dataSources", [])
        ]

        return DataSourceListResponse(
            data_sources=data_sources,
            total=data.get("total", 0),
            skip=data.get("skip", 0),
            limit=data.get("limit", 0),
        )

    async def get(self, data_source_id: str) -> DataSource:
        """
        Get data source details by ID.

        Retrieves complete data source information including configuration,
        connection details, and settings.

        Args:
            data_source_id: The unique identifier of the data source.

        Returns:
            DataSource object with complete details including config.

        Example:
            >>> ds = await sdk.data_source.get("api-sales-data")
            >>> print(f"Name: {ds.name}")
            >>> print(f"Type: {ds.type}")
            >>> print(f"Config: {ds.config}")
        """
        query = """
        query GetDataSource($dataSourceId: String!) {
            dataSource(dataSourceId: $dataSourceId) {
                id
                dataSourceId
                name
                type
                config
                cacheTtl
                retryPolicy
                isPublic
                createdAt
                updatedAt
            }
        }
        """

        variables = {"dataSourceId": data_source_id}
        response = await self.client.request(query, variables)
        data = response["dataSource"]

        return DataSource(
            id=data["id"],
            data_source_id=data["dataSourceId"],
            name=data["name"],
            type=data["type"],
            config=data.get("config"),
            cache_ttl=data.get("cacheTtl"),
            retry_policy=data.get("retryPolicy"),
            is_public=data.get("isPublic", False),
            created_at=data.get("createdAt"),
            updated_at=data.get("updatedAt"),
        )

    async def create(self, input_data: CreateDataSourceInput) -> CreateDataSourceResponse:
        """
        Create a new data source.

        Creates a new data source with the specified type, configuration,
        and connection settings.

        Args:
            input_data: Data source creation input with required and optional fields.

        Returns:
            CreateDataSourceResponse with success status and created data source.

        Example:
            >>> input_data = CreateDataSourceInput(
            ...     data_source_id="api-customer-data",
            ...     name="Customer API",
            ...     type="rest",
            ...     config={
            ...         "url": "https://api.example.com/customers",
            ...         "method": "GET",
            ...         "headers": {"Authorization": "Bearer token"}
            ...     },
            ...     cache_ttl=300,
            ...     is_public=False
            ... )
            >>> result = await sdk.data_source.create(input_data)
            >>> if result.success:
            ...     print(f"Data source created: {result.data_source.data_source_id}")
        """
        mutation = """
        mutation CreateDataSource($input: CreateDataSourceInput!) {
            createDataSource(input: $input) {
                success
                message
                dataSource {
                    id
                    dataSourceId
                    name
                    type
                    isPublic
                    createdAt
                }
            }
        }
        """

        variables = {
            "input": {
                "dataSourceId": input_data.data_source_id,
                "name": input_data.name,
                "type": input_data.type,
                "config": input_data.config,
            }
        }

        if input_data.cache_ttl is not None:
            variables["input"]["cacheTtl"] = input_data.cache_ttl
        if input_data.is_public is not None:
            variables["input"]["isPublic"] = input_data.is_public

        response = await self.client.request(mutation, variables)
        data = response["createDataSource"]

        ds_data = data.get("dataSource", {})
        data_source = DataSource(
            id=ds_data.get("id", ""),
            data_source_id=ds_data.get("dataSourceId", ""),
            name=ds_data.get("name", ""),
            type=ds_data.get("type", ""),
            config=None,
            cache_ttl=None,
            retry_policy=None,
            is_public=ds_data.get("isPublic", False),
            created_at=ds_data.get("createdAt"),
            updated_at=None,
        )

        return CreateDataSourceResponse(
            success=data["success"],
            message=data.get("message"),
            data_source=data_source,
        )

    async def update(
        self, data_source_id: str, input_data: UpdateDataSourceInput
    ) -> UpdateDataSourceResponse:
        """
        Update an existing data source.

        Updates data source properties including name, type, configuration,
        and cache settings.

        Args:
            data_source_id: The ID of the data source to update.
            input_data: Data source update input with fields to modify.

        Returns:
            UpdateDataSourceResponse with success status and updated data source.

        Example:
            >>> input_data = UpdateDataSourceInput(
            ...     name="Customer API v2",
            ...     config={
            ...         "url": "https://api.example.com/v2/customers",
            ...         "method": "GET"
            ...     },
            ...     cache_ttl=600
            ... )
            >>> result = await sdk.data_source.update("api-customer-data", input_data)
            >>> if result.success:
            ...     print(f"Data source updated: {result.data_source.name}")
        """
        mutation = """
        mutation UpdateDataSource($dataSourceId: String!, $input: UpdateDataSourceInput!) {
            updateDataSource(dataSourceId: $dataSourceId, input: $input) {
                success
                message
                dataSource {
                    id
                    dataSourceId
                    name
                    type
                    updatedAt
                }
            }
        }
        """

        variables: Dict[str, Any] = {"dataSourceId": data_source_id, "input": {}}

        if input_data.name is not None:
            variables["input"]["name"] = input_data.name
        if input_data.type is not None:
            variables["input"]["type"] = input_data.type
        if input_data.config is not None:
            variables["input"]["config"] = input_data.config
        if input_data.cache_ttl is not None:
            variables["input"]["cacheTtl"] = input_data.cache_ttl

        response = await self.client.request(mutation, variables)
        data = response["updateDataSource"]

        ds_data = data.get("dataSource", {})
        data_source = DataSource(
            id=ds_data.get("id", ""),
            data_source_id=ds_data.get("dataSourceId", ""),
            name=ds_data.get("name", ""),
            type=ds_data.get("type", ""),
            config=None,
            cache_ttl=None,
            retry_policy=None,
            is_public=False,
            created_at=None,
            updated_at=ds_data.get("updatedAt"),
        )

        return UpdateDataSourceResponse(
            success=data["success"],
            message=data.get("message"),
            data_source=data_source,
        )

    async def delete(self, data_source_id: str) -> DeleteDataSourceResponse:
        """
        Delete a data source.

        Permanently removes a data source. Note that this may affect
        dashboards and widgets using this data source.

        Args:
            data_source_id: The ID of the data source to delete.

        Returns:
            DeleteDataSourceResponse with success status and message.

        Example:
            >>> result = await sdk.data_source.delete("old-api-source")
            >>> if result.success:
            ...     print("Data source deleted successfully")

        Warning:
            This operation is irreversible and may break dependent widgets.
            Ensure the data source is not in use before deleting.
        """
        mutation = """
        mutation DeleteDataSource($dataSourceId: String!) {
            deleteDataSource(dataSourceId: $dataSourceId) {
                success
                message
            }
        }
        """

        variables = {"dataSourceId": data_source_id}
        response = await self.client.request(mutation, variables)
        data = response["deleteDataSource"]

        return DeleteDataSourceResponse(
            success=data["success"],
            message=data.get("message"),
        )

    async def test_connection(
        self, data_source_id: str, params: Optional[Dict[str, Any]] = None
    ) -> TestDataSourceResponse:
        """
        Test an existing data source connection.

        Validates that the data source can be successfully connected to
        and optionally tests with specific parameters.

        Args:
            data_source_id: The ID of the data source to test.
            params: Optional test parameters (e.g., query filters, limits).

        Returns:
            TestDataSourceResponse with success status, message, and sample data.

        Example:
            >>> # Test connection without parameters
            >>> result = await sdk.data_source.test_connection("api-customer-data")
            >>> if result.success:
            ...     print("Connection successful!")
            ...     print(f"Sample data: {result.data}")

            >>> # Test with specific parameters
            >>> result = await sdk.data_source.test_connection(
            ...     "api-customer-data",
            ...     params={"limit": 5}
            ... )
        """
        mutation = """
        mutation TestDataSource($dataSourceId: String!, $params: JSON) {
            testDataSource(dataSourceId: $dataSourceId, params: $params) {
                success
                message
                data
            }
        }
        """

        variables: Dict[str, Any] = {"dataSourceId": data_source_id}
        if params is not None:
            variables["params"] = params

        response = await self.client.request(mutation, variables)
        data = response["testDataSource"]

        return TestDataSourceResponse(
            success=data["success"],
            message=data.get("message"),
            data=data.get("data"),
        )

    async def fetch_data(self, data_source_id: str) -> DataSourceData:
        """
        Fetch data from a data source.

        Retrieves actual data from the data source, respecting cache
        settings and retry policies.

        Args:
            data_source_id: The ID of the data source to fetch from.

        Returns:
            DataSourceData with fetched data, metadata, and status.

        Example:
            >>> data = await sdk.data_source.fetch_data("api-sales-data")
            >>> if data.success:
            ...     print(f"Source: {data.source}")
            ...     print(f"Timestamp: {data.timestamp}")
            ...     print(f"Data: {data.data}")
            >>> else:
            ...     print(f"Error: {data.error}")
        """
        query = """
        query FetchDataSourceData($dataSourceId: String!) {
            dataSourceData(dataSourceId: $dataSourceId) {
                success
                data
                source
                timestamp
                error
            }
        }
        """

        variables = {"dataSourceId": data_source_id}
        response = await self.client.request(query, variables)
        data = response["dataSourceData"]

        return DataSourceData(
            success=data["success"],
            data=data.get("data"),
            source=data.get("source"),
            timestamp=data.get("timestamp"),
            error=data.get("error"),
        )

    async def batch_fetch(self, data_source_ids: List[str]) -> Dict[str, Any]:
        """
        Fetch data from multiple data sources in a single request.

        Efficiently retrieves data from multiple data sources simultaneously,
        useful for dashboard rendering or bulk operations.

        Args:
            data_source_ids: List of data source IDs to fetch from.

        Returns:
            Dictionary with success status and results for each data source.

        Example:
            >>> result = await sdk.data_source.batch_fetch([
            ...     "api-sales-data",
            ...     "api-customer-data",
            ...     "api-inventory-data"
            ... ])
            >>> if result["success"]:
            ...     for ds_id, ds_data in result["results"].items():
            ...         print(f"{ds_id}: {ds_data}")
        """
        query = """
        query BatchFetchDataSources($dataSourceIds: [String!]!) {
            batchDataSourcesData(dataSourceIds: $dataSourceIds) {
                success
                results
            }
        }
        """

        variables = {"dataSourceIds": data_source_ids}
        response = await self.client.request(query, variables)
        return response["batchDataSourcesData"]
