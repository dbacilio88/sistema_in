"""
Reporting module for traffic analysis system.

This module provides comprehensive reporting and dashboard capabilities including:
- Automated report generation
- Real-time dashboards
- Data visualization
- Performance analytics
- Export utilities
"""

from .report_generator import (
    ReportGenerator,
    ReportConfig,
    ReportType,
    TrafficMetrics,
    ViolationSummary,
    DeviceMetrics,
    TrafficDataAnalyzer,
    DashboardManager
)

from .dashboard_service import (
    DashboardService,
    DashboardConfig,
    Alert,
    AlertLevel,
    AlertType,
    DashboardCLI
)

from .visualization_utils import (
    AdvancedChartGenerator,
    ChartConfig,
    VisualizationTheme,
    DataExporter,
    CHART_TEMPLATES
)

from .api_server import (
    ReportingAPIServer,
    ReportRequest,
    ChartRequest,
    MetricsResponse,
    ReportResponse
)


__all__ = [
    # Report generation
    'ReportGenerator',
    'ReportConfig', 
    'ReportType',
    'TrafficMetrics',
    'ViolationSummary',
    'DeviceMetrics',
    'TrafficDataAnalyzer',
    
    # Dashboard services
    'DashboardManager',
    'DashboardService',
    'DashboardConfig',
    'DashboardCLI',
    
    # Alerts
    'Alert',
    'AlertLevel',
    'AlertType',
    
    # Visualization
    'AdvancedChartGenerator',
    'ChartConfig',
    'VisualizationTheme',
    'DataExporter',
    'CHART_TEMPLATES',
    
    # API server
    'ReportingAPIServer',
    'ReportRequest',
    'ChartRequest', 
    'MetricsResponse',
    'ReportResponse'
]


# Module version
__version__ = "1.0.0"


# Default configurations
DEFAULT_REPORT_CONFIG = ReportConfig(
    report_type=ReportType.DAILY_SUMMARY,
    start_date=None,  # Will be set at runtime
    end_date=None,    # Will be set at runtime
    include_charts=True,
    output_format="html"
)

DEFAULT_DASHBOARD_CONFIG = DashboardConfig(
    refresh_interval=5,
    chart_update_interval=10,
    auto_refresh=True,
    theme="light"
)

DEFAULT_CHART_CONFIG = ChartConfig(
    theme=VisualizationTheme.DEFAULT,
    width=800,
    height=600,
    interactive=False
)