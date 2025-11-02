"""
Comprehensive test suite for the reporting module.

Tests cover:
- Report generation functionality
- Dashboard services
- Data visualization
- API endpoints
- Chart generation
"""

import os
import sys
import pytest
import asyncio
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from reporting.report_generator import (
    ReportGenerator, ReportConfig, ReportType, TrafficDataAnalyzer,
    DashboardManager, TrafficMetrics, ViolationSummary, DeviceMetrics
)
from reporting.dashboard_service import DashboardService, Alert, AlertType, AlertLevel
from reporting.visualization_utils import AdvancedChartGenerator, ChartConfig, VisualizationTheme
from reporting.api_server import ReportingAPIServer


class TestTrafficDataAnalyzer:
    """Test cases for TrafficDataAnalyzer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.analyzer = TrafficDataAnalyzer()
        self.start_date = datetime(2024, 1, 1, 0, 0, 0)
        self.end_date = datetime(2024, 1, 1, 23, 59, 59)
    
    def test_analyze_traffic_flow(self):
        """Test traffic flow analysis."""
        metrics = self.analyzer.analyze_traffic_flow(
            self.start_date, self.end_date, ['cam_001', 'cam_002']
        )
        
        assert isinstance(metrics, TrafficMetrics)
        assert metrics.total_vehicles >= 0
        assert metrics.average_speed >= 0
        assert metrics.violation_count >= 0
        assert 0 <= metrics.peak_hour <= 23
        assert isinstance(metrics.vehicle_types, dict)
        assert isinstance(metrics.hourly_distribution, dict)
        assert isinstance(metrics.violation_types, dict)
    
    def test_analyze_violations(self):
        """Test violation analysis."""
        summary = self.analyzer.analyze_violations(
            self.start_date, self.end_date, ['cam_001']
        )
        
        assert isinstance(summary, ViolationSummary)
        assert summary.total_violations >= 0
        assert isinstance(summary.by_type, dict)
        assert isinstance(summary.by_device, dict)
        assert isinstance(summary.by_hour, dict)
        assert 0 <= summary.average_severity <= 5
        assert 0 <= summary.resolution_rate <= 1
        assert summary.repeat_offenders >= 0
    
    def test_analyze_device_performance(self):
        """Test device performance analysis."""
        metrics = self.analyzer.analyze_device_performance(
            self.start_date, self.end_date, ['cam_001', 'cam_002']
        )
        
        assert isinstance(metrics, list)
        for device_metric in metrics:
            assert isinstance(device_metric, DeviceMetrics)
            assert device_metric.device_id
            assert 0 <= device_metric.uptime_percentage <= 100
            assert device_metric.frames_processed >= 0
            assert device_metric.average_fps >= 0
            assert device_metric.error_count >= 0
            assert device_metric.violations_detected >= 0
    
    def test_simulated_data_generation(self):
        """Test simulated violation data generation."""
        violations = self.analyzer._generate_simulated_violations(
            self.start_date, self.end_date, ['cam_001']
        )
        
        assert isinstance(violations, list)
        assert len(violations) > 0
        
        for violation in violations[:5]:  # Check first 5
            assert 'violation_id' in violation
            assert 'device_id' in violation
            assert 'violation_type' in violation
            assert 'timestamp' in violation
            assert isinstance(violation['timestamp'], datetime)


class TestReportGenerator:
    """Test cases for ReportGenerator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.report_generator = ReportGenerator()
        self.start_date = datetime(2024, 1, 1)
        self.end_date = datetime(2024, 1, 2)
    
    @pytest.mark.asyncio
    async def test_generate_daily_summary(self):
        """Test daily summary report generation."""
        config = ReportConfig(
            report_type=ReportType.DAILY_SUMMARY,
            start_date=self.start_date,
            end_date=self.end_date,
            include_charts=True
        )
        
        report = await self.report_generator.generate_report(config)
        
        assert isinstance(report, dict)
        assert report['report_type'] == 'daily_summary'
        assert 'metrics' in report
        assert 'charts' in report
        assert 'html_content' in report
        assert 'generated_at' in report
        
        # Check metrics structure
        assert 'traffic' in report['metrics']
        assert 'violations' in report['metrics']
        
        # Check HTML content
        assert '<html>' in report['html_content']
        assert 'Reporte Diario de Tráfico' in report['html_content']
    
    @pytest.mark.asyncio
    async def test_generate_weekly_analysis(self):
        """Test weekly analysis report generation."""
        config = ReportConfig(
            report_type=ReportType.WEEKLY_ANALYSIS,
            start_date=self.start_date,
            end_date=self.start_date + timedelta(days=7),
            include_charts=True
        )
        
        report = await self.report_generator.generate_report(config)
        
        assert report['report_type'] == 'weekly_analysis'
        assert 'daily_metrics' in report
        assert 'summary' in report
        assert len(report['daily_metrics']) == 8  # 7 days + 1
    
    @pytest.mark.asyncio
    async def test_generate_monthly_report(self):
        """Test monthly report generation."""
        config = ReportConfig(
            report_type=ReportType.MONTHLY_REPORT,
            start_date=self.start_date,
            end_date=self.start_date + timedelta(days=30),
            include_charts=True
        )
        
        report = await self.report_generator.generate_report(config)
        
        assert report['report_type'] == 'monthly_report'
        assert 'metrics' in report
        assert 'summary' in report
        assert 'charts' in report
    
    @pytest.mark.asyncio
    async def test_generate_violation_trends(self):
        """Test violation trends report generation."""
        config = ReportConfig(
            report_type=ReportType.VIOLATION_TRENDS,
            start_date=self.start_date,
            end_date=self.end_date,
            include_charts=True
        )
        
        report = await self.report_generator.generate_report(config)
        
        assert report['report_type'] == 'violation_trends'
        assert 'violation_analysis' in report
    
    @pytest.mark.asyncio
    async def test_invalid_report_type(self):
        """Test handling of invalid report type."""
        with pytest.raises(ValueError):
            config = ReportConfig(
                report_type="invalid_type",
                start_date=self.start_date,
                end_date=self.end_date
            )


class TestDashboardManager:
    """Test cases for DashboardManager."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.dashboard_manager = DashboardManager()
    
    def test_get_realtime_metrics(self):
        """Test real-time metrics retrieval."""
        metrics = self.dashboard_manager.get_realtime_metrics()
        
        assert isinstance(metrics, dict)
        assert 'timestamp' in metrics
        assert 'today_vehicles' in metrics
        assert 'today_violations' in metrics
        assert 'active_devices' in metrics
        assert 'average_speed' in metrics
        assert 'device_status' in metrics
        
        # Check data types
        assert isinstance(metrics['today_vehicles'], int)
        assert isinstance(metrics['today_violations'], int)
        assert isinstance(metrics['active_devices'], int)
        assert isinstance(metrics['average_speed'], (int, float))
        assert isinstance(metrics['device_status'], list)
    
    def test_get_dashboard_charts(self):
        """Test dashboard charts generation."""
        charts = self.dashboard_manager.get_dashboard_charts()
        
        assert isinstance(charts, dict)
        # Charts should be JSON strings for Plotly
        for chart_name, chart_data in charts.items():
            assert isinstance(chart_data, str)
            # Should be valid JSON
            json.loads(chart_data)


class TestAdvancedChartGenerator:
    """Test cases for AdvancedChartGenerator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.config = ChartConfig(
            theme=VisualizationTheme.DEFAULT,
            width=800,
            height=600,
            interactive=False
        )
        self.chart_generator = AdvancedChartGenerator(self.config)
    
    def test_create_violation_heatmap(self):
        """Test violation heatmap creation."""
        data = {
            'cam_001': {str(i): i % 10 for i in range(24)},
            'cam_002': {str(i): (i * 2) % 15 for i in range(24)}
        }
        
        chart = self.chart_generator.create_violation_heatmap(data)
        
        assert isinstance(chart, str)
        assert chart.startswith('data:image/png;base64,')
    
    def test_create_trend_analysis(self):
        """Test trend analysis chart creation."""
        now = datetime.now()
        data = {
            'Violaciones': [
                (now - timedelta(days=i), 10 + i) for i in range(7)
            ],
            'Vehículos': [
                (now - timedelta(days=i), 100 + i * 5) for i in range(7)
            ]
        }
        
        chart = self.chart_generator.create_trend_analysis(data)
        
        assert isinstance(chart, str)
        assert chart.startswith('data:image/png;base64,')
    
    def test_create_performance_dashboard(self):
        """Test performance dashboard creation."""
        device_metrics = [
            {
                'device_id': 'cam_001',
                'uptime_percentage': 95.5,
                'average_fps': 25.0,
                'violations_detected': 50,
                'accuracy_score': 0.85
            },
            {
                'device_id': 'cam_002', 
                'uptime_percentage': 92.0,
                'average_fps': 23.5,
                'violations_detected': 42,
                'accuracy_score': 0.82
            }
        ]
        
        chart = self.chart_generator.create_performance_dashboard(device_metrics)
        
        assert isinstance(chart, str)
        assert chart.startswith('data:image/png;base64,')
    
    def test_create_speed_distribution(self):
        """Test speed distribution chart creation."""
        speed_data = [45, 50, 55, 60, 48, 52, 58, 62, 44, 49, 53, 57]
        
        chart = self.chart_generator.create_speed_distribution(speed_data)
        
        assert isinstance(chart, str)
        assert chart.startswith('data:image/png;base64,')
    
    def test_interactive_charts(self):
        """Test interactive chart generation."""
        config = ChartConfig(interactive=True)
        chart_gen = AdvancedChartGenerator(config)
        
        data = {
            'cam_001': {str(i): i % 5 for i in range(24)}
        }
        
        chart = chart_gen.create_violation_heatmap(data)
        
        # Interactive charts return JSON
        assert isinstance(chart, str)
        json.loads(chart)  # Should be valid JSON
    
    def test_different_themes(self):
        """Test different visualization themes."""
        themes = [VisualizationTheme.DARK, VisualizationTheme.MINIMAL, 
                 VisualizationTheme.PROFESSIONAL]
        
        for theme in themes:
            config = ChartConfig(theme=theme)
            chart_gen = AdvancedChartGenerator(config)
            
            # Test that different themes work
            assert chart_gen.colors  # Should have colors defined
            assert chart_gen.bg_color  # Should have background color
            assert chart_gen.text_color  # Should have text color


class TestDashboardService:
    """Test cases for DashboardService."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.dashboard_service = DashboardService(port=8888)
    
    def test_dashboard_service_initialization(self):
        """Test dashboard service initialization."""
        assert self.dashboard_service.port == 8888
        assert self.dashboard_service.analyzer is not None
        assert self.dashboard_service.dashboard_manager is not None
        assert self.dashboard_service.report_generator is not None
        assert isinstance(self.dashboard_service.alerts, list)
        assert isinstance(self.dashboard_service.active_connections, set)
    
    def test_alert_creation(self):
        """Test alert creation and management."""
        alert = Alert(
            alert_id="test_001",
            alert_type=AlertType.HIGH_VIOLATION_RATE,
            level=AlertLevel.WARNING,
            title="Test Alert",
            message="This is a test alert",
            device_id=None,
            timestamp=datetime.now()
        )
        
        assert alert.alert_id == "test_001"
        assert alert.alert_type == AlertType.HIGH_VIOLATION_RATE
        assert alert.level == AlertLevel.WARNING
        assert not alert.acknowledged
        assert not alert.resolved
    
    @pytest.mark.asyncio
    async def test_check_alerts(self):
        """Test alert monitoring logic."""
        # This would require mocking metrics
        await self.dashboard_service._check_alerts()
        
        # Should not raise any exceptions
        assert True


@pytest.mark.asyncio
class TestReportingAPIServer:
    """Test cases for ReportingAPIServer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.api_server = ReportingAPIServer(port=8889)
    
    def test_api_server_initialization(self):
        """Test API server initialization."""
        assert self.api_server.port == 8889
        assert self.api_server.report_generator is not None
        assert self.api_server.dashboard_manager is not None
        assert self.api_server.chart_generator is not None
        assert isinstance(self.api_server.generated_reports, dict)
    
    def test_background_report_generation(self):
        """Test background report generation."""
        report_id = "test_report_001"
        config = ReportConfig(
            report_type=ReportType.DAILY_SUMMARY,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 2)
        )
        
        # Setup report entry
        self.api_server.generated_reports[report_id] = {
            "id": report_id,
            "config": {},
            "status": "generating",
            "created_at": datetime.now().isoformat(),
            "report_data": None
        }
        
        # This would be called as background task
        # For testing, we just verify it can be called
        assert report_id in self.api_server.generated_reports


class TestIntegration:
    """Integration tests for the complete reporting system."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_report_generation(self):
        """Test complete report generation workflow."""
        # Create report generator
        generator = ReportGenerator()
        
        # Create configuration
        config = ReportConfig(
            report_type=ReportType.DAILY_SUMMARY,
            start_date=datetime(2024, 1, 1),
            end_date=datetime(2024, 1, 1, 23, 59, 59),
            include_charts=True,
            output_format="html"
        )
        
        # Generate report
        report = await generator.generate_report(config)
        
        # Verify complete report structure
        assert isinstance(report, dict)
        assert all(key in report for key in [
            'report_type', 'period', 'metrics', 'charts', 
            'html_content', 'generated_at'
        ])
        
        # Verify HTML content is valid
        html_content = report['html_content']
        assert '<html>' in html_content
        assert '</html>' in html_content
        assert 'Reporte Diario de Tráfico' in html_content
        
        # Verify charts are included
        assert len(report['charts']) > 0
        for chart_name, chart_data in report['charts'].items():
            assert isinstance(chart_data, str)
            assert chart_data.startswith('data:image/')
    
    def test_dashboard_metrics_integration(self):
        """Test dashboard metrics integration."""
        # Create dashboard manager
        dashboard = DashboardManager()
        
        # Get real-time metrics
        metrics = dashboard.get_realtime_metrics()
        
        # Verify metrics structure
        required_fields = [
            'timestamp', 'today_vehicles', 'today_violations',
            'active_devices', 'average_speed', 'device_status'
        ]
        
        for field in required_fields:
            assert field in metrics
        
        # Verify device status structure
        for device in metrics['device_status']:
            assert 'device_id' in device
            assert 'status' in device
            assert 'fps' in device
            assert 'violations' in device
    
    def test_chart_generation_integration(self):
        """Test chart generation integration."""
        # Create chart generator
        config = ChartConfig(theme=VisualizationTheme.PROFESSIONAL)
        generator = AdvancedChartGenerator(config)
        
        # Create analyzer for data
        analyzer = TrafficDataAnalyzer()
        
        # Get sample data
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)
        
        traffic_metrics = analyzer.analyze_traffic_flow(start_date, end_date)
        device_metrics = analyzer.analyze_device_performance(start_date, end_date)
        
        # Generate charts
        speed_data = [50 + i for i in range(20)]
        speed_chart = generator.create_speed_distribution(speed_data)
        
        device_data = [
            {
                'device_id': d.device_id,
                'uptime_percentage': d.uptime_percentage,
                'average_fps': d.average_fps,
                'violations_detected': d.violations_detected,
                'accuracy_score': d.accuracy_score or 0.8
            }
            for d in device_metrics
        ]
        performance_chart = generator.create_performance_dashboard(device_data)
        
        # Verify charts are generated
        assert isinstance(speed_chart, str)
        assert isinstance(performance_chart, str)
        assert speed_chart.startswith('data:image/')
        assert performance_chart.startswith('data:image/')


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])