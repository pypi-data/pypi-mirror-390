"""Type definitions for AI module."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class AITimeRange:
    """Time range for AI analysis."""

    start: str
    end: str


@dataclass
class AIAnalyzeDashboardResponse:
    """Response from AI dashboard analysis."""

    analysis: str
    suggestions: List[str]
    insights: List[str]
    generated_at: Optional[str] = None


@dataclass
class AIPerformanceAnalysis:
    """AI-powered performance analysis results."""

    current_metrics: Optional[Dict[str, Any]]
    optimizations: List[str]
    estimated_impact: Optional[Dict[str, Any]]


@dataclass
class AISmartAlert:
    """Individual smart alert from AI analysis."""

    id: str
    type: str
    severity: str
    message: str
    timestamp: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class AISmartAlertsResponse:
    """Response containing smart alerts."""

    alerts: List[AISmartAlert]


@dataclass
class AIDataInsight:
    """Data insight discovered by AI."""

    type: str
    description: str
    confidence: float
    data: Optional[Dict[str, Any]] = None
    priority: Optional[str] = None


@dataclass
class AIExplainDataResponse:
    """Response from AI data explanation."""

    explanation: str
    key_insights: List[str]
    trends: List[str]
    recommendations: List[str]


@dataclass
class AIRecommendationContext:
    """Context for AI widget recommendations."""

    dashboard_id: Optional[str] = None
    category: Optional[str] = None
    user_role: Optional[str] = None


@dataclass
class AIWidgetRecommendation:
    """AI-powered widget recommendation."""

    widget_type: str
    description: str
    config: Optional[Dict[str, Any]] = None
    rationale: Optional[str] = None


@dataclass
class AIOptimizeDashboardInput:
    """Input for dashboard optimization."""

    dashboard_id: str
    goals: List[str]


@dataclass
class AIOptimizeDashboardResponse:
    """Response from dashboard optimization."""

    success: bool
    message: Optional[str] = None
    optimized_config: Optional[Dict[str, Any]] = None
    changes: List[str] = None


@dataclass
class AIGenerateTemplateInput:
    """Input for template generation."""

    industry: str
    role: str
    goals: List[str]


@dataclass
class AIGenerateTemplateResponse:
    """Response from template generation."""

    success: bool
    message: Optional[str] = None
    template: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None
    alternatives: List[Dict[str, Any]] = None


@dataclass
class ColorPreferences:
    """Color preferences for palette generation."""

    theme: Optional[str] = None
    high_contrast: Optional[bool] = None


@dataclass
class ColorPalette:
    """Color palette suggestion."""

    name: str
    colors: List[str]
    description: Optional[str] = None


@dataclass
class AIColorPaletteSuggestions:
    """AI-powered color palette suggestions."""

    palettes: List[ColorPalette]


@dataclass
class AIAccessibilityAnalysis:
    """AI-powered accessibility analysis results."""

    score: float
    issues: List[Dict[str, Any]]
    improvements: List[str]


@dataclass
class AIQueryInput:
    """Input for AI query."""

    query: str
    dashboard_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


@dataclass
class AIQueryResponse:
    """Response from AI query."""

    response: str
    confidence: float
    sources: List[str]
    suggestions: List[str]
