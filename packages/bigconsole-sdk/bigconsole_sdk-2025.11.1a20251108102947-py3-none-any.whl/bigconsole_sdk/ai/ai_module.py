"""
AI Module for BigConsole SDK.

This module provides AI-powered analytics and insights functionality including:
- Dashboard analysis and optimization
- Performance analysis
- Smart alerts and anomaly detection
- Data insights and explanations
- Widget recommendations
- Template generation
- Color palette suggestions
- Accessibility analysis
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ..types.ai import (
    AIAccessibilityAnalysis,
    AIAnalyzeDashboardResponse,
    AIColorPaletteSuggestions,
    AIDataInsight,
    AIExplainDataResponse,
    AIGenerateTemplateInput,
    AIGenerateTemplateResponse,
    AIOptimizeDashboardInput,
    AIOptimizeDashboardResponse,
    AIPerformanceAnalysis,
    AIQueryInput,
    AIQueryResponse,
    AIRecommendationContext,
    AISmartAlert,
    AISmartAlertsResponse,
    AITimeRange,
    AIWidgetRecommendation,
    ColorPalette,
    ColorPreferences,
)

if TYPE_CHECKING:
    from ..client.base_client import BaseGraphQLClient


class AIModule:
    """
    AI Module for BigConsole SDK.

    Provides AI-powered analytics, insights, and optimization capabilities
    for dashboards, widgets, and data sources.
    """

    def __init__(self, client: "BaseGraphQLClient") -> None:
        """
        Initialize AI module.

        Args:
            client: The GraphQL client instance for making requests.
        """
        self.client = client

    async def analyze_dashboard(self, dashboard_id: str) -> AIAnalyzeDashboardResponse:
        """
        Get AI-powered dashboard analysis and optimization suggestions.

        Analyzes dashboard layout, widgets, and configurations to provide
        comprehensive insights and improvement suggestions.

        Args:
            dashboard_id: The ID of the dashboard to analyze.

        Returns:
            AIAnalyzeDashboardResponse containing analysis, suggestions, and insights.

        Example:
            >>> analysis = await sdk.ai.analyze_dashboard("dashboard-123")
            >>> print(analysis.analysis)
            >>> for suggestion in analysis.suggestions:
            ...     print(suggestion)
        """
        query = """
        query AIAnalyzeDashboard($dashboardId: String!) {
            aiAnalyzeDashboard(dashboardId: $dashboardId) {
                analysis
                suggestions
                insights
                generatedAt
            }
        }
        """

        variables = {"dashboardId": dashboard_id}
        response = await self.client.request(query, variables)
        data = response["aiAnalyzeDashboard"]

        return AIAnalyzeDashboardResponse(
            analysis=data["analysis"],
            suggestions=data.get("suggestions", []),
            insights=data.get("insights", []),
            generated_at=data.get("generatedAt"),
        )

    async def performance_analysis(self, dashboard_id: str) -> AIPerformanceAnalysis:
        """
        Get AI-powered performance metrics and optimization recommendations.

        Analyzes dashboard performance including load times, rendering speed,
        and provides optimization recommendations.

        Args:
            dashboard_id: The ID of the dashboard to analyze.

        Returns:
            AIPerformanceAnalysis with current metrics and optimizations.

        Example:
            >>> perf = await sdk.ai.performance_analysis("dashboard-123")
            >>> print(perf.current_metrics)
            >>> print(perf.optimizations)
        """
        query = """
        query AIPerformanceAnalysis($dashboardId: String!) {
            aiPerformanceAnalysis(dashboardId: $dashboardId) {
                currentMetrics
                optimizations
                estimatedImpact
            }
        }
        """

        variables = {"dashboardId": dashboard_id}
        response = await self.client.request(query, variables)
        data = response["aiPerformanceAnalysis"]

        return AIPerformanceAnalysis(
            current_metrics=data.get("currentMetrics"),
            optimizations=data.get("optimizations", []),
            estimated_impact=data.get("estimatedImpact"),
        )

    async def smart_alerts(
        self, dashboard_id: str, time_range: Optional[AITimeRange] = None
    ) -> AISmartAlertsResponse:
        """
        Detect anomalies and get smart alerts with AI.

        Analyzes dashboard data to detect anomalies, unusual patterns,
        and generate intelligent alerts.

        Args:
            dashboard_id: The ID of the dashboard to monitor.
            time_range: Optional time range for analysis (start and end timestamps).

        Returns:
            AISmartAlertsResponse containing detected alerts.

        Example:
            >>> from datetime import datetime, timedelta
            >>> time_range = AITimeRange(
            ...     start=(datetime.now() - timedelta(days=7)).isoformat(),
            ...     end=datetime.now().isoformat()
            ... )
            >>> alerts = await sdk.ai.smart_alerts("dashboard-123", time_range)
            >>> for alert in alerts.alerts:
            ...     print(f"{alert.severity}: {alert.message}")
        """
        query = """
        query AISmartAlerts($dashboardId: String!, $timeRange: AITimeRangeInput) {
            aiSmartAlerts(dashboardId: $dashboardId, timeRange: $timeRange) {
                alerts {
                    id
                    type
                    severity
                    message
                    timestamp
                    data
                }
            }
        }
        """

        variables: Dict[str, Any] = {"dashboardId": dashboard_id}
        if time_range:
            variables["timeRange"] = {
                "start": time_range.start,
                "end": time_range.end,
            }

        response = await self.client.request(query, variables)
        data = response["aiSmartAlerts"]

        alerts = [
            AISmartAlert(
                id=alert["id"],
                type=alert["type"],
                severity=alert["severity"],
                message=alert["message"],
                timestamp=alert.get("timestamp"),
                data=alert.get("data"),
            )
            for alert in data.get("alerts", [])
        ]

        return AISmartAlertsResponse(alerts=alerts)

    async def data_insights(
        self, data_source_id: str, time_range: Optional[AITimeRange] = None
    ) -> List[AIDataInsight]:
        """
        Get AI insights for data patterns and trends.

        Analyzes data source to identify patterns, trends, correlations,
        and other meaningful insights.

        Args:
            data_source_id: The ID of the data source to analyze.
            time_range: Optional time range for analysis.

        Returns:
            List of AIDataInsight objects with discovered insights.

        Example:
            >>> insights = await sdk.ai.data_insights("datasource-123")
            >>> for insight in insights:
            ...     print(
            ...         f"{insight.type}: {insight.description} "
            ...         f"(confidence: {insight.confidence})"
            ...     )
        """
        query = """
        query AIDataInsights($dataSourceId: String!, $timeRange: AITimeRangeInput) {
            aiDataInsights(dataSourceId: $dataSourceId, timeRange: $timeRange) {
                type
                description
                confidence
                data
                priority
            }
        }
        """

        variables: Dict[str, Any] = {"dataSourceId": data_source_id}
        if time_range:
            variables["timeRange"] = {
                "start": time_range.start,
                "end": time_range.end,
            }

        response = await self.client.request(query, variables)
        insights_data = response["aiDataInsights"]

        # Handle both single object and array responses
        if isinstance(insights_data, dict):
            insights_data = [insights_data]

        return [
            AIDataInsight(
                type=insight["type"],
                description=insight["description"],
                confidence=insight.get("confidence", 0.0),
                data=insight.get("data"),
                priority=insight.get("priority"),
            )
            for insight in insights_data
        ]

    async def explain_data(
        self, data_source_id: str, widget_id: str, query: Optional[str] = None
    ) -> AIExplainDataResponse:
        """
        Generate natural language explanations for data.

        Provides human-readable explanations of data patterns, trends,
        and key insights for a specific widget and data source.

        Args:
            data_source_id: The ID of the data source.
            widget_id: The ID of the widget displaying the data.
            query: Optional specific question about the data.

        Returns:
            AIExplainDataResponse with explanations and recommendations.

        Example:
            >>> explanation = await sdk.ai.explain_data(
            ...     "datasource-123",
            ...     "widget-456",
            ...     "Why did sales spike on Tuesday?"
            ... )
            >>> print(explanation.explanation)
            >>> for insight in explanation.key_insights:
            ...     print(insight)
        """
        graphql_query = """
        query AIExplainData($dataSourceId: String!, $widgetId: String!, $query: String) {
            aiExplainData(dataSourceId: $dataSourceId, widgetId: $widgetId, query: $query) {
                explanation
                keyInsights
                trends
                recommendations
            }
        }
        """

        variables: Dict[str, Any] = {
            "dataSourceId": data_source_id,
            "widgetId": widget_id,
        }
        if query:
            variables["query"] = query

        response = await self.client.request(graphql_query, variables)
        data = response["aiExplainData"]

        return AIExplainDataResponse(
            explanation=data["explanation"],
            key_insights=data.get("keyInsights", []),
            trends=data.get("trends", []),
            recommendations=data.get("recommendations", []),
        )

    async def widget_recommendations(
        self, data_sources: List[str], context: Optional[AIRecommendationContext] = None
    ) -> List[AIWidgetRecommendation]:
        """
        Get AI-powered widget type recommendations.

        Analyzes data sources and context to recommend the most appropriate
        widget types and configurations.

        Args:
            data_sources: List of data source IDs to analyze.
            context: Optional context including dashboard ID, category, user role.

        Returns:
            List of AIWidgetRecommendation with suggested widgets.

        Example:
            >>> context = AIRecommendationContext(
            ...     dashboard_id="dashboard-123",
            ...     category="analytics",
            ...     user_role="analyst"
            ... )
            >>> recommendations = await sdk.ai.widget_recommendations(
            ...     ["datasource-1", "datasource-2"],
            ...     context
            ... )
            >>> for rec in recommendations:
            ...     widget_info = f"{rec.widget_type}: {rec.description}"
            ...     print(widget_info)
        """
        query = """
        query AIWidgetRecommendations(
            $dataSources: [String!]!,
            $context: AIRecommendationContextInput
        ) {
            aiWidgetRecommendations(
                dataSources: $dataSources,
                context: $context
            ) {
                widgetType
                description
                config
                rationale
            }
        }
        """

        variables: Dict[str, Any] = {"dataSources": data_sources}
        if context:
            context_dict: Dict[str, Any] = {}
            if context.dashboard_id:
                context_dict["dashboardId"] = context.dashboard_id
            if context.category:
                context_dict["category"] = context.category
            if context.user_role:
                context_dict["userRole"] = context.user_role
            if context_dict:
                variables["context"] = context_dict

        response = await self.client.request(query, variables)
        recommendations_data = response["aiWidgetRecommendations"]

        # Handle both single object and array responses
        if isinstance(recommendations_data, dict):
            recommendations_data = [recommendations_data]

        return [
            AIWidgetRecommendation(
                widget_type=rec["widgetType"],
                description=rec["description"],
                config=rec.get("config"),
                rationale=rec.get("rationale"),
            )
            for rec in recommendations_data
        ]

    async def optimize_dashboard(
        self, input_data: AIOptimizeDashboardInput
    ) -> AIOptimizeDashboardResponse:
        """
        Auto-optimize dashboard layout and configuration with AI.

        Applies AI-driven optimizations to dashboard configuration based
        on specified goals (e.g., performance, usability, accessibility).

        Args:
            input_data: Optimization input with dashboard ID and goals.

        Returns:
            AIOptimizeDashboardResponse with optimized config and changes.

        Example:
            >>> input_data = AIOptimizeDashboardInput(
            ...     dashboard_id="dashboard-123",
            ...     goals=["performance", "accessibility", "user_engagement"]
            ... )
            >>> result = await sdk.ai.optimize_dashboard(input_data)
            >>> if result.success:
            ...     print(result.optimized_config)
            ...     for change in result.changes:
            ...         print(change)
        """
        mutation = """
        mutation AIOptimizeDashboard($input: AIOptimizeDashboardInput!) {
            aiOptimizeDashboard(input: $input) {
                success
                message
                optimizedConfig
                changes
            }
        }
        """

        variables = {
            "input": {
                "dashboardId": input_data.dashboard_id,
                "goals": input_data.goals,
            }
        }

        response = await self.client.request(mutation, variables)
        data = response["aiOptimizeDashboard"]

        return AIOptimizeDashboardResponse(
            success=data["success"],
            message=data.get("message"),
            optimized_config=data.get("optimizedConfig"),
            changes=data.get("changes", []),
        )

    async def generate_template(
        self, input_data: AIGenerateTemplateInput
    ) -> AIGenerateTemplateResponse:
        """
        Generate dashboard template based on requirements using AI.

        Creates a complete dashboard template including layout, widgets,
        and configurations based on industry, role, and goals.

        Args:
            input_data: Template generation input with industry, role, and goals.

        Returns:
            AIGenerateTemplateResponse with generated template and alternatives.

        Example:
            >>> input_data = AIGenerateTemplateInput(
            ...     industry="e-commerce",
            ...     role="product_manager",
            ...     goals=["track_kpis", "monitor_conversions", "analyze_trends"]
            ... )
            >>> result = await sdk.ai.generate_template(input_data)
            >>> if result.success:
            ...     print(result.template)
            ...     print(result.explanation)
        """
        mutation = """
        mutation AIGenerateTemplate($input: AIGenerateTemplateInput!) {
            aiGenerateDashboardTemplate(input: $input) {
                success
                message
                template
                explanation
                alternatives
            }
        }
        """

        variables = {
            "input": {
                "industry": input_data.industry,
                "role": input_data.role,
                "goals": input_data.goals,
            }
        }

        response = await self.client.request(mutation, variables)
        data = response["aiGenerateDashboardTemplate"]

        return AIGenerateTemplateResponse(
            success=data["success"],
            message=data.get("message"),
            template=data.get("template"),
            explanation=data.get("explanation"),
            alternatives=data.get("alternatives", []),
        )

    async def color_palette_suggestions(
        self, dashboard_id: str, preferences: Optional[ColorPreferences] = None
    ) -> AIColorPaletteSuggestions:
        """
        Get AI-powered color palette suggestions for a dashboard.

        Generates color palettes optimized for readability, accessibility,
        and visual appeal based on dashboard content and user preferences.

        Args:
            dashboard_id: The ID of the dashboard.
            preferences: Optional color preferences (theme, contrast, etc.).

        Returns:
            AIColorPaletteSuggestions with multiple palette options.

        Example:
            >>> preferences = ColorPreferences(
            ...     theme="dark",
            ...     high_contrast=True
            ... )
            >>> suggestions = await sdk.ai.color_palette_suggestions(
            ...     "dashboard-123",
            ...     preferences
            ... )
            >>> for palette in suggestions.palettes:
            ...     print(f"{palette.name}: {palette.colors}")
        """
        query = """
        query AIColorPalette($dashboardId: String!, $preferences: AIColorPreferencesInput) {
            aiColorPaletteSuggestions(dashboardId: $dashboardId, preferences: $preferences) {
                palettes {
                    name
                    colors
                    description
                }
            }
        }
        """

        variables: Dict[str, Any] = {"dashboardId": dashboard_id}
        if preferences:
            pref_dict: Dict[str, Any] = {}
            if preferences.theme:
                pref_dict["theme"] = preferences.theme
            if preferences.high_contrast is not None:
                pref_dict["highContrast"] = preferences.high_contrast
            if pref_dict:
                variables["preferences"] = pref_dict

        response = await self.client.request(query, variables)
        data = response["aiColorPaletteSuggestions"]

        palettes = [
            ColorPalette(
                name=palette["name"],
                colors=palette["colors"],
                description=palette.get("description"),
            )
            for palette in data.get("palettes", [])
        ]

        return AIColorPaletteSuggestions(palettes=palettes)

    async def accessibility_analysis(self, dashboard_id: str) -> AIAccessibilityAnalysis:
        """
        Get AI-powered accessibility analysis for a dashboard.

        Analyzes dashboard for accessibility issues including color contrast,
        text readability, keyboard navigation, and WCAG compliance.

        Args:
            dashboard_id: The ID of the dashboard to analyze.

        Returns:
            AIAccessibilityAnalysis with score, issues, and improvements.

        Example:
            >>> analysis = await sdk.ai.accessibility_analysis("dashboard-123")
            >>> print(f"Accessibility Score: {analysis.score}/100")
            >>> for issue in analysis.issues:
            ...     print(f"{issue['severity']}: {issue['description']}")
            ...     print(f"Fix: {issue['fix']}")
        """
        query = """
        query AIAccessibilityAnalysis($dashboardId: String!) {
            aiAccessibilityAnalysis(dashboardId: $dashboardId) {
                score
                issues {
                    severity
                    description
                    location
                    fix
                }
                improvements
            }
        }
        """

        variables = {"dashboardId": dashboard_id}
        response = await self.client.request(query, variables)
        data = response["aiAccessibilityAnalysis"]

        return AIAccessibilityAnalysis(
            score=data["score"],
            issues=data.get("issues", []),
            improvements=data.get("improvements", []),
        )

    async def query(self, input_data: AIQueryInput) -> AIQueryResponse:
        """
        Send a natural language query to AI for analysis.

        Process arbitrary questions about dashboards, data, or analytics
        using natural language.

        Args:
            input_data: AI query input with question and context.

        Returns:
            AIQueryResponse with answer, confidence, and suggestions.

        Example:
            >>> input_data = AIQueryInput(
            ...     query="What are the top performing products this month?",
            ...     dashboard_id="dashboard-123"
            ... )
            >>> result = await sdk.ai.query(input_data)
            >>> print(result.response)
            >>> print(f"Confidence: {result.confidence}")
        """
        mutation = """
        mutation AIQuery($input: AIQueryInput!) {
            aiQuery(input: $input) {
                response
                confidence
                sources
                suggestions
            }
        }
        """

        variables = {
            "input": {
                "query": input_data.query,
            }
        }

        if input_data.dashboard_id:
            variables["input"]["dashboardId"] = input_data.dashboard_id
        if input_data.context:
            variables["input"]["context"] = input_data.context

        response = await self.client.request(mutation, variables)
        data = response["aiQuery"]

        return AIQueryResponse(
            response=data["response"],
            confidence=data.get("confidence", 0.0),
            sources=data.get("sources", []),
            suggestions=data.get("suggestions", []),
        )
