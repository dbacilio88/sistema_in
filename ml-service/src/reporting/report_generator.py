"""
Traffic analysis reporting and dashboard system.

This module provides comprehensive reporting capabilities including:
- Traffic flow analysis and reports
- Violation statistics and trends
- Performance dashboards
- Custom report generation
- Data visualization components
"""

import os
import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import calendar

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from matplotlib.backends.backend_agg import FigureCanvasAgg
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils


logger = logging.getLogger(__name__)


class ReportType(Enum):
    """Report type enumeration."""
    DAILY_SUMMARY = "daily_summary"
    WEEKLY_ANALYSIS = "weekly_analysis"
    MONTHLY_REPORT = "monthly_report"
    VIOLATION_TRENDS = "violation_trends"
    DEVICE_PERFORMANCE = "device_performance"
    TRAFFIC_FLOW = "traffic_flow"
    CUSTOM = "custom"


class ChartType(Enum):
    """Chart type enumeration."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    HEATMAP = "heatmap"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    BOX = "box"
    AREA = "area"


@dataclass
class ReportConfig:
    """Configuration for report generation."""
    report_type: ReportType
    start_date: datetime
    end_date: datetime
    device_ids: Optional[List[str]] = None
    violation_types: Optional[List[str]] = None
    include_charts: bool = True
    include_raw_data: bool = False
    output_format: str = "html"  # html, pdf, json
    chart_style: str = "default"  # default, dark, minimal
    language: str = "es"  # es, en


@dataclass
class TrafficMetrics:
    """Traffic analysis metrics."""
    total_vehicles: int
    average_speed: float
    violation_count: int
    peak_hour: int
    vehicle_types: Dict[str, int]
    hourly_distribution: Dict[int, int]
    violation_types: Dict[str, int]
    device_uptime: float


@dataclass
class ViolationSummary:
    """Violation summary statistics."""
    total_violations: int
    by_type: Dict[str, int]
    by_device: Dict[str, int]
    by_hour: Dict[int, int]
    average_severity: float
    resolution_rate: float
    repeat_offenders: int


@dataclass
class DeviceMetrics:
    """Device performance metrics."""
    device_id: str
    uptime_percentage: float
    frames_processed: int
    average_fps: float
    error_count: int
    last_active: datetime
    violations_detected: int
    accuracy_score: Optional[float] = None


class TrafficDataAnalyzer:
    """Analyzer for traffic data and metrics."""
    
    def __init__(self, storage_service=None):
        self.storage_service = storage_service
        
    def analyze_traffic_flow(self, start_date: datetime, end_date: datetime,
                           device_ids: List[str] = None) -> TrafficMetrics:
        """Analyze traffic flow patterns."""
        # Get violation records for analysis
        violations = self._get_violations_data(start_date, end_date, device_ids)
        
        if not violations:
            return TrafficMetrics(
                total_vehicles=0,
                average_speed=0.0,
                violation_count=0,
                peak_hour=12,
                vehicle_types={},
                hourly_distribution={},
                violation_types={},
                device_uptime=0.0
            )
        
        # Analyze violations data
        total_vehicles = len(set(v.get('license_plate', f"unknown_{i}") 
                               for i, v in enumerate(violations) if v.get('license_plate')))
        
        speeds = [v['speed_kmh'] for v in violations if v.get('speed_kmh')]
        average_speed = statistics.mean(speeds) if speeds else 0.0
        
        # Hourly distribution
        hourly_dist = {}
        for v in violations:
            hour = v['timestamp'].hour
            hourly_dist[hour] = hourly_dist.get(hour, 0) + 1
        
        peak_hour = max(hourly_dist.keys(), key=lambda h: hourly_dist[h]) if hourly_dist else 12
        
        # Vehicle types distribution
        vehicle_types = {}
        for v in violations:
            vtype = v.get('vehicle_class', 'unknown')
            vehicle_types[vtype] = vehicle_types.get(vtype, 0) + 1
        
        # Violation types distribution
        violation_types = {}
        for v in violations:
            vtype = v.get('violation_type', 'unknown')
            violation_types[vtype] = violation_types.get(vtype, 0) + 1
        
        return TrafficMetrics(
            total_vehicles=total_vehicles,
            average_speed=average_speed,
            violation_count=len(violations),
            peak_hour=peak_hour,
            vehicle_types=vehicle_types,
            hourly_distribution=hourly_dist,
            violation_types=violation_types,
            device_uptime=95.0  # Simulated uptime
        )
    
    def analyze_violations(self, start_date: datetime, end_date: datetime,
                          device_ids: List[str] = None) -> ViolationSummary:
        """Analyze violation patterns and statistics."""
        violations = self._get_violations_data(start_date, end_date, device_ids)
        
        if not violations:
            return ViolationSummary(
                total_violations=0,
                by_type={},
                by_device={},
                by_hour={},
                average_severity=0.0,
                resolution_rate=0.0,
                repeat_offenders=0
            )
        
        # Violations by type
        by_type = {}
        for v in violations:
            vtype = v.get('violation_type', 'unknown')
            by_type[vtype] = by_type.get(vtype, 0) + 1
        
        # Violations by device
        by_device = {}
        for v in violations:
            device = v.get('device_id', 'unknown')
            by_device[device] = by_device.get(device, 0) + 1
        
        # Violations by hour
        by_hour = {}
        for v in violations:
            hour = v['timestamp'].hour
            by_hour[hour] = by_hour.get(hour, 0) + 1
        
        # Calculate repeat offenders (same license plate)
        plates = [v.get('license_plate') for v in violations if v.get('license_plate')]
        plate_counts = {}
        for plate in plates:
            plate_counts[plate] = plate_counts.get(plate, 0) + 1
        
        repeat_offenders = sum(1 for count in plate_counts.values() if count > 1)
        
        return ViolationSummary(
            total_violations=len(violations),
            by_type=by_type,
            by_device=by_device,
            by_hour=by_hour,
            average_severity=2.5,  # Simulated severity (1-5 scale)
            resolution_rate=0.85,  # Simulated resolution rate
            repeat_offenders=repeat_offenders
        )
    
    def analyze_device_performance(self, start_date: datetime, end_date: datetime,
                                 device_ids: List[str] = None) -> List[DeviceMetrics]:
        """Analyze device performance metrics."""
        violations = self._get_violations_data(start_date, end_date, device_ids)
        
        # Group by device
        devices = {}
        for v in violations:
            device_id = v.get('device_id', 'unknown')
            if device_id not in devices:
                devices[device_id] = []
            devices[device_id].append(v)
        
        device_metrics = []
        for device_id, device_violations in devices.items():
            # Calculate metrics
            frames_processed = len(device_violations) * 30  # Estimate 30 frames per detection
            
            processing_times = [v.get('processing_time_ms', 150) 
                              for v in device_violations]
            avg_processing_time = statistics.mean(processing_times) if processing_times else 150
            average_fps = 1000 / avg_processing_time if avg_processing_time > 0 else 6.7
            
            # Accuracy based on confidence scores
            confidences = [v.get('confidence', 0.8) for v in device_violations]
            accuracy_score = statistics.mean(confidences) if confidences else 0.8
            
            # Last activity
            timestamps = [v['timestamp'] for v in device_violations]
            last_active = max(timestamps) if timestamps else start_date
            
            device_metrics.append(DeviceMetrics(
                device_id=device_id,
                uptime_percentage=95.0 + (hash(device_id) % 10),  # Simulated uptime
                frames_processed=frames_processed,
                average_fps=average_fps,
                error_count=hash(device_id) % 5,  # Simulated error count
                last_active=last_active,
                violations_detected=len(device_violations),
                accuracy_score=accuracy_score
            ))
        
        return device_metrics
    
    def _get_violations_data(self, start_date: datetime, end_date: datetime,
                           device_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Get violations data from storage."""
        if self.storage_service:
            violations = self.storage_service.get_violation_records(
                start_time=start_date,
                end_time=end_date,
                limit=10000
            )
            
            # Filter by device IDs if specified
            if device_ids:
                violations = [v for v in violations if v.get('device_id') in device_ids]
            
            return violations
        else:
            # Generate simulated data for testing
            return self._generate_simulated_violations(start_date, end_date, device_ids)
    
    def _generate_simulated_violations(self, start_date: datetime, end_date: datetime,
                                     device_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Generate simulated violation data for testing."""
        violations = []
        
        if not device_ids:
            device_ids = ['cam_001', 'cam_002', 'cam_003']
        
        violation_types = ['speed', 'red_light', 'lane_violation', 'illegal_turn']
        vehicle_classes = ['car', 'truck', 'motorcycle', 'bus']
        
        # Generate violations for each day
        current_date = start_date
        while current_date <= end_date:
            # Generate 20-50 violations per day
            daily_violations = 20 + (hash(str(current_date.date())) % 30)
            
            for i in range(daily_violations):
                # Random time during the day (more during peak hours)
                hour = np.random.choice(
                    range(24), 
                    p=[0.02, 0.01, 0.01, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.08,
                       0.06, 0.07, 0.08, 0.09, 0.08, 0.07, 0.09, 0.12, 0.10, 0.08,
                       0.06, 0.04, 0.03, 0.02]
                )
                
                violation_time = current_date.replace(
                    hour=hour,
                    minute=np.random.randint(0, 60),
                    second=np.random.randint(0, 60)
                )
                
                violation = {
                    'violation_id': f"V{current_date.strftime('%Y%m%d')}_{i:03d}",
                    'device_id': np.random.choice(device_ids),
                    'violation_type': np.random.choice(violation_types),
                    'timestamp': violation_time,
                    'vehicle_bbox': [100, 100, 200, 200],
                    'vehicle_class': np.random.choice(vehicle_classes),
                    'confidence': 0.7 + np.random.random() * 0.3,
                    'speed_kmh': 40 + np.random.normal(20, 10) if np.random.random() > 0.3 else None,
                    'processing_time_ms': 100 + np.random.normal(50, 20),
                    'license_plate': f"ABC{np.random.randint(100, 999)}" if np.random.random() > 0.3 else None
                }
                
                violations.append(violation)
            
            current_date += timedelta(days=1)
        
        return violations


class ChartGenerator:
    """Generator for various types of charts and visualizations."""
    
    def __init__(self, style: str = "default"):
        self.style = style
        self._setup_style()
    
    def _setup_style(self):
        """Setup chart styling."""
        if self.style == "dark":
            plt.style.use('dark_background')
            self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8']
        elif self.style == "minimal":
            plt.style.use('seaborn-v0_8-minimal')
            self.colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#593E40']
        else:
            plt.style.use('default')
            self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
    
    def create_line_chart(self, data: Dict[str, List], title: str, 
                         x_label: str, y_label: str) -> str:
        """Create line chart."""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for i, (label, values) in enumerate(data.items()):
            ax.plot(values, label=label, color=self.colors[i % len(self.colors)], linewidth=2)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save to base64 string
        return self._fig_to_base64(fig)
    
    def create_bar_chart(self, data: Dict[str, Union[int, float]], title: str,
                        x_label: str, y_label: str) -> str:
        """Create bar chart."""
        fig, ax = plt.subplots(figsize=(10, 6))
        
        labels = list(data.keys())
        values = list(data.values())
        
        bars = ax.bar(labels, values, color=self.colors[:len(labels)])
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value}', ha='center', va='bottom')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel(x_label, fontsize=12)
        ax.set_ylabel(y_label, fontsize=12)
        
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def create_pie_chart(self, data: Dict[str, Union[int, float]], title: str) -> str:
        """Create pie chart."""
        fig, ax = plt.subplots(figsize=(8, 8))
        
        labels = list(data.keys())
        values = list(data.values())
        
        # Calculate percentages
        total = sum(values)
        percentages = [v/total*100 for v in values]
        
        wedges, texts, autotexts = ax.pie(
            values, 
            labels=labels, 
            autopct='%1.1f%%',
            colors=self.colors[:len(labels)],
            startangle=90
        )
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def create_heatmap(self, data: List[List[float]], x_labels: List[str],
                      y_labels: List[str], title: str) -> str:
        """Create heatmap."""
        fig, ax = plt.subplots(figsize=(12, 8))
        
        im = ax.imshow(data, cmap='YlOrRd', aspect='auto')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(x_labels)))
        ax.set_yticks(np.arange(len(y_labels)))
        ax.set_xticklabels(x_labels)
        ax.set_yticklabels(y_labels)
        
        # Rotate x labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        
        # Add text annotations
        for i in range(len(y_labels)):
            for j in range(len(x_labels)):
                text = ax.text(j, i, f'{data[i][j]:.0f}',
                             ha="center", va="center", color="black")
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        
        return self._fig_to_base64(fig)
    
    def create_time_series_chart(self, timestamps: List[datetime], values: List[float],
                               title: str, y_label: str) -> str:
        """Create time series chart."""
        fig, ax = plt.subplots(figsize=(14, 6))
        
        ax.plot(timestamps, values, color=self.colors[0], linewidth=2, marker='o', markersize=4)
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_ylabel(y_label, fontsize=12)
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def create_plotly_interactive_chart(self, data: Dict[str, Any], chart_type: str) -> str:
        """Create interactive Plotly chart."""
        if chart_type == "line":
            fig = go.Figure()
            
            for label, values in data.items():
                if isinstance(values, list):
                    fig.add_trace(go.Scatter(
                        y=values,
                        mode='lines+markers',
                        name=label,
                        line=dict(width=3)
                    ))
            
            fig.update_layout(
                title=data.get('title', 'Interactive Chart'),
                xaxis_title=data.get('x_label', 'X Axis'),
                yaxis_title=data.get('y_label', 'Y Axis'),
                hovermode='x unified'
            )
        
        elif chart_type == "bar":
            fig = px.bar(
                x=list(data['values'].keys()),
                y=list(data['values'].values()),
                title=data.get('title', 'Bar Chart')
            )
        
        elif chart_type == "pie":
            fig = px.pie(
                values=list(data['values'].values()),
                names=list(data['values'].keys()),
                title=data.get('title', 'Pie Chart')
            )
        
        # Return JSON representation
        return plotly.utils.PlotlyJSONEncoder().encode(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        import io
        import base64
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f"data:image/png;base64,{image_base64}"


class ReportGenerator:
    """Main report generator class."""
    
    def __init__(self, storage_service=None):
        self.storage_service = storage_service
        self.analyzer = TrafficDataAnalyzer(storage_service)
        self.chart_generator = ChartGenerator()
        
        # Load templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load HTML templates for reports."""
        templates = {}
        
        # Base HTML template
        templates['base'] = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 40px; 
                    background-color: #f5f5f5;
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    background-color: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 40px;
                    border-bottom: 3px solid #2E86AB;
                    padding-bottom: 20px;
                }}
                .section {{ 
                    margin-bottom: 40px; 
                }}
                .metrics-grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 20px; 
                    margin-bottom: 30px;
                }}
                .metric-card {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 20px; 
                    border-radius: 10px;
                    text-align: center;
                }}
                .metric-value {{ 
                    font-size: 2.5em; 
                    font-weight: bold;
                    display: block;
                }}
                .metric-label {{ 
                    font-size: 1.1em; 
                    opacity: 0.9;
                }}
                .chart-container {{ 
                    text-align: center; 
                    margin: 30px 0;
                    background-color: #fafafa;
                    padding: 20px;
                    border-radius: 10px;
                }}
                .chart {{ 
                    max-width: 100%; 
                    height: auto;
                }}
                h1 {{ 
                    color: #2E86AB; 
                    font-size: 2.5em;
                }}
                h2 {{ 
                    color: #333; 
                    border-bottom: 2px solid #eee;
                    padding-bottom: 10px;
                }}
                .footer {{ 
                    text-align: center; 
                    margin-top: 40px; 
                    color: #666;
                    font-size: 0.9em;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 12px;
                    text-align: left;
                }}
                th {{
                    background-color: #2E86AB;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                    <p><strong>Período:</strong> {period} | <strong>Generado:</strong> {generated_at}</p>
                </div>
                {content}
                <div class="footer">
                    <p>Sistema de Análisis de Tráfico - Reporte Generado Automáticamente</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return templates
    
    async def generate_report(self, config: ReportConfig) -> Dict[str, Any]:
        """Generate report based on configuration."""
        logger.info(f"Generating {config.report_type.value} report for {config.start_date} to {config.end_date}")
        
        if config.report_type == ReportType.DAILY_SUMMARY:
            return await self._generate_daily_summary(config)
        elif config.report_type == ReportType.WEEKLY_ANALYSIS:
            return await self._generate_weekly_analysis(config)
        elif config.report_type == ReportType.MONTHLY_REPORT:
            return await self._generate_monthly_report(config)
        elif config.report_type == ReportType.VIOLATION_TRENDS:
            return await self._generate_violation_trends(config)
        elif config.report_type == ReportType.DEVICE_PERFORMANCE:
            return await self._generate_device_performance(config)
        elif config.report_type == ReportType.TRAFFIC_FLOW:
            return await self._generate_traffic_flow_report(config)
        else:
            raise ValueError(f"Unsupported report type: {config.report_type}")
    
    async def _generate_daily_summary(self, config: ReportConfig) -> Dict[str, Any]:
        """Generate daily summary report."""
        # Analyze data
        traffic_metrics = self.analyzer.analyze_traffic_flow(
            config.start_date, config.end_date, config.device_ids
        )
        violation_summary = self.analyzer.analyze_violations(
            config.start_date, config.end_date, config.device_ids
        )
        
        # Generate charts
        charts = {}
        if config.include_charts:
            # Hourly violations chart
            charts['hourly_violations'] = self.chart_generator.create_bar_chart(
                traffic_metrics.hourly_distribution,
                "Distribución de Violaciones por Hora",
                "Hora del Día", "Número de Violaciones"
            )
            
            # Violation types pie chart
            charts['violation_types'] = self.chart_generator.create_pie_chart(
                violation_summary.by_type,
                "Distribución de Tipos de Violaciones"
            )
            
            # Vehicle types chart
            charts['vehicle_types'] = self.chart_generator.create_bar_chart(
                traffic_metrics.vehicle_types,
                "Distribución de Tipos de Vehículos",
                "Tipo de Vehículo", "Cantidad"
            )
        
        # Build content
        content_sections = []
        
        # Summary metrics
        content_sections.append(f"""
        <div class="section">
            <h2>Resumen Ejecutivo</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">{traffic_metrics.total_vehicles}</span>
                    <span class="metric-label">Vehículos Detectados</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{violation_summary.total_violations}</span>
                    <span class="metric-label">Total Violaciones</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{traffic_metrics.average_speed:.1f}</span>
                    <span class="metric-label">Velocidad Promedio (km/h)</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{traffic_metrics.peak_hour}:00</span>
                    <span class="metric-label">Hora Pico</span>
                </div>
            </div>
        </div>
        """)
        
        # Add charts
        if config.include_charts:
            for chart_name, chart_data in charts.items():
                content_sections.append(f"""
                <div class="section">
                    <div class="chart-container">
                        <img src="{chart_data}" class="chart" alt="{chart_name}">
                    </div>
                </div>
                """)
        
        # Generate HTML
        html_content = self.templates['base'].format(
            title="Reporte Diario de Tráfico",
            period=f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            content='\n'.join(content_sections)
        )
        
        return {
            "report_type": config.report_type.value,
            "period": f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            "metrics": {
                "traffic": asdict(traffic_metrics),
                "violations": asdict(violation_summary)
            },
            "charts": charts if config.include_charts else {},
            "html_content": html_content,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _generate_weekly_analysis(self, config: ReportConfig) -> Dict[str, Any]:
        """Generate weekly analysis report."""
        # Analyze data day by day for trend analysis
        daily_metrics = []
        current_date = config.start_date
        
        while current_date <= config.end_date:
            day_end = current_date.replace(hour=23, minute=59, second=59)
            
            day_traffic = self.analyzer.analyze_traffic_flow(
                current_date, day_end, config.device_ids
            )
            day_violations = self.analyzer.analyze_violations(
                current_date, day_end, config.device_ids
            )
            
            daily_metrics.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_name': current_date.strftime('%A'),
                'vehicles': day_traffic.total_vehicles,
                'violations': day_violations.total_violations,
                'avg_speed': day_traffic.average_speed
            })
            
            current_date += timedelta(days=1)
        
        # Generate trend charts
        charts = {}
        if config.include_charts:
            # Daily violations trend
            violation_trend = {day['date']: day['violations'] for day in daily_metrics}
            charts['weekly_violations'] = self.chart_generator.create_line_chart(
                {'Violaciones Diarias': list(violation_trend.values())},
                "Tendencia Semanal de Violaciones",
                "Días", "Número de Violaciones"
            )
            
            # Vehicle detection trend
            vehicle_trend = {day['date']: day['vehicles'] for day in daily_metrics}
            charts['weekly_vehicles'] = self.chart_generator.create_line_chart(
                {'Vehículos Detectados': list(vehicle_trend.values())},
                "Tendencia Semanal de Detección de Vehículos",
                "Días", "Número de Vehículos"
            )
        
        # Calculate weekly totals
        total_vehicles = sum(day['vehicles'] for day in daily_metrics)
        total_violations = sum(day['violations'] for day in daily_metrics)
        avg_speed = statistics.mean([day['avg_speed'] for day in daily_metrics if day['avg_speed'] > 0])
        
        # Build content
        content_sections = []
        
        # Weekly summary
        content_sections.append(f"""
        <div class="section">
            <h2>Resumen Semanal</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">{total_vehicles}</span>
                    <span class="metric-label">Total Vehículos</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{total_violations}</span>
                    <span class="metric-label">Total Violaciones</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{avg_speed:.1f}</span>
                    <span class="metric-label">Velocidad Promedio (km/h)</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{len(daily_metrics)}</span>
                    <span class="metric-label">Días Analizados</span>
                </div>
            </div>
        </div>
        """)
        
        # Daily breakdown table
        content_sections.append(f"""
        <div class="section">
            <h2>Desglose Diario</h2>
            <table>
                <thead>
                    <tr>
                        <th>Fecha</th>
                        <th>Día</th>
                        <th>Vehículos</th>
                        <th>Violaciones</th>
                        <th>Velocidad Promedio</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([
                        f"<tr><td>{day['date']}</td><td>{day['day_name']}</td><td>{day['vehicles']}</td><td>{day['violations']}</td><td>{day['avg_speed']:.1f} km/h</td></tr>"
                        for day in daily_metrics
                    ])}
                </tbody>
            </table>
        </div>
        """)
        
        # Add charts
        if config.include_charts:
            for chart_name, chart_data in charts.items():
                content_sections.append(f"""
                <div class="section">
                    <div class="chart-container">
                        <img src="{chart_data}" class="chart" alt="{chart_name}">
                    </div>
                </div>
                """)
        
        # Generate HTML
        html_content = self.templates['base'].format(
            title="Análisis Semanal de Tráfico",
            period=f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            content='\n'.join(content_sections)
        )
        
        return {
            "report_type": config.report_type.value,
            "period": f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            "daily_metrics": daily_metrics,
            "summary": {
                "total_vehicles": total_vehicles,
                "total_violations": total_violations,
                "average_speed": avg_speed
            },
            "charts": charts if config.include_charts else {},
            "html_content": html_content,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _generate_monthly_report(self, config: ReportConfig) -> Dict[str, Any]:
        """Generate monthly comprehensive report."""
        # Get comprehensive analysis
        traffic_metrics = self.analyzer.analyze_traffic_flow(
            config.start_date, config.end_date, config.device_ids
        )
        violation_summary = self.analyzer.analyze_violations(
            config.start_date, config.end_date, config.device_ids
        )
        device_metrics = self.analyzer.analyze_device_performance(
            config.start_date, config.end_date, config.device_ids
        )
        
        # Generate comprehensive charts
        charts = {}
        if config.include_charts:
            # Monthly violation heatmap (hour vs day)
            days_in_month = (config.end_date - config.start_date).days + 1
            heatmap_data = []
            
            for hour in range(24):
                hour_data = []
                for day in range(days_in_month):
                    # Simulate violation count for each hour/day combination
                    base_violations = traffic_metrics.hourly_distribution.get(hour, 0)
                    day_factor = 0.5 + (hash(f"{hour}_{day}") % 100) / 100
                    hour_data.append(int(base_violations * day_factor / days_in_month))
                heatmap_data.append(hour_data)
            
            charts['monthly_heatmap'] = self.chart_generator.create_heatmap(
                heatmap_data,
                [f"Día {i+1}" for i in range(min(days_in_month, 31))],
                [f"{h:02d}:00" for h in range(24)],
                "Mapa de Calor: Violaciones por Hora y Día"
            )
            
            # Device performance comparison
            device_names = [d.device_id for d in device_metrics]
            device_violations = [d.violations_detected for d in device_metrics]
            charts['device_performance'] = self.chart_generator.create_bar_chart(
                dict(zip(device_names, device_violations)),
                "Rendimiento de Dispositivos - Violaciones Detectadas",
                "Dispositivo", "Violaciones"
            )
        
        # Calculate additional monthly metrics
        days_analyzed = (config.end_date - config.start_date).days + 1
        avg_violations_per_day = violation_summary.total_violations / days_analyzed if days_analyzed > 0 else 0
        avg_vehicles_per_day = traffic_metrics.total_vehicles / days_analyzed if days_analyzed > 0 else 0
        
        # Build content
        content_sections = []
        
        # Executive summary
        content_sections.append(f"""
        <div class="section">
            <h2>Resumen Ejecutivo Mensual</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">{traffic_metrics.total_vehicles}</span>
                    <span class="metric-label">Total Vehículos</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{violation_summary.total_violations}</span>
                    <span class="metric-label">Total Violaciones</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{avg_violations_per_day:.1f}</span>
                    <span class="metric-label">Promedio Violaciones/Día</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{violation_summary.repeat_offenders}</span>
                    <span class="metric-label">Reincidentes</span>
                </div>
            </div>
        </div>
        """)
        
        # Device performance table
        content_sections.append(f"""
        <div class="section">
            <h2>Rendimiento de Dispositivos</h2>
            <table>
                <thead>
                    <tr>
                        <th>Dispositivo</th>
                        <th>Uptime (%)</th>
                        <th>FPS Promedio</th>
                        <th>Violaciones</th>
                        <th>Precisión</th>
                        <th>Última Actividad</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([
                        f"<tr><td>{d.device_id}</td><td>{d.uptime_percentage:.1f}%</td><td>{d.average_fps:.1f}</td><td>{d.violations_detected}</td><td>{d.accuracy_score:.2f}</td><td>{d.last_active.strftime('%Y-%m-%d %H:%M')}</td></tr>"
                        for d in device_metrics
                    ])}
                </tbody>
            </table>
        </div>
        """)
        
        # Add charts
        if config.include_charts:
            for chart_name, chart_data in charts.items():
                content_sections.append(f"""
                <div class="section">
                    <div class="chart-container">
                        <img src="{chart_data}" class="chart" alt="{chart_name}">
                    </div>
                </div>
                """)
        
        # Generate HTML
        html_content = self.templates['base'].format(
            title="Reporte Mensual de Tráfico",
            period=f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            content='\n'.join(content_sections)
        )
        
        return {
            "report_type": config.report_type.value,
            "period": f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            "metrics": {
                "traffic": asdict(traffic_metrics),
                "violations": asdict(violation_summary),
                "devices": [asdict(d) for d in device_metrics]
            },
            "summary": {
                "days_analyzed": days_analyzed,
                "avg_violations_per_day": avg_violations_per_day,
                "avg_vehicles_per_day": avg_vehicles_per_day
            },
            "charts": charts if config.include_charts else {},
            "html_content": html_content,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _generate_violation_trends(self, config: ReportConfig) -> Dict[str, Any]:
        """Generate violation trends analysis report."""
        violation_summary = self.analyzer.analyze_violations(
            config.start_date, config.end_date, config.device_ids
        )
        
        # Generate trend charts
        charts = {}
        if config.include_charts:
            # Violation types distribution
            charts['violation_types'] = self.chart_generator.create_pie_chart(
                violation_summary.by_type,
                "Distribución de Tipos de Violaciones"
            )
            
            # Violations by device
            charts['violations_by_device'] = self.chart_generator.create_bar_chart(
                violation_summary.by_device,
                "Violaciones por Dispositivo",
                "Dispositivo", "Número de Violaciones"
            )
            
            # Hourly pattern
            charts['hourly_pattern'] = self.chart_generator.create_line_chart(
                {'Violaciones por Hora': [violation_summary.by_hour.get(h, 0) for h in range(24)]},
                "Patrón Horario de Violaciones",
                "Hora del Día", "Número de Violaciones"
            )
        
        # Build content for violation trends
        content_sections = []
        
        content_sections.append(f"""
        <div class="section">
            <h2>Análisis de Tendencias de Violaciones</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">{violation_summary.total_violations}</span>
                    <span class="metric-label">Total Violaciones</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{len(violation_summary.by_type)}</span>
                    <span class="metric-label">Tipos de Violaciones</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{violation_summary.resolution_rate:.1%}</span>
                    <span class="metric-label">Tasa de Resolución</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{violation_summary.repeat_offenders}</span>
                    <span class="metric-label">Reincidentes</span>
                </div>
            </div>
        </div>
        """)
        
        # Add charts
        if config.include_charts:
            for chart_name, chart_data in charts.items():
                content_sections.append(f"""
                <div class="section">
                    <div class="chart-container">
                        <img src="{chart_data}" class="chart" alt="{chart_name}">
                    </div>
                </div>
                """)
        
        html_content = self.templates['base'].format(
            title="Análisis de Tendencias de Violaciones",
            period=f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            content='\n'.join(content_sections)
        )
        
        return {
            "report_type": config.report_type.value,
            "period": f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            "violation_analysis": asdict(violation_summary),
            "charts": charts if config.include_charts else {},
            "html_content": html_content,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _generate_device_performance(self, config: ReportConfig) -> Dict[str, Any]:
        """Generate device performance report."""
        device_metrics = self.analyzer.analyze_device_performance(
            config.start_date, config.end_date, config.device_ids
        )
        
        # Generate performance charts
        charts = {}
        if config.include_charts:
            # Uptime comparison
            device_names = [d.device_id for d in device_metrics]
            uptime_values = [d.uptime_percentage for d in device_metrics]
            charts['uptime_comparison'] = self.chart_generator.create_bar_chart(
                dict(zip(device_names, uptime_values)),
                "Comparación de Uptime por Dispositivo",
                "Dispositivo", "Uptime (%)"
            )
            
            # FPS performance
            fps_values = [d.average_fps for d in device_metrics]
            charts['fps_performance'] = self.chart_generator.create_bar_chart(
                dict(zip(device_names, fps_values)),
                "Rendimiento FPS por Dispositivo",
                "Dispositivo", "FPS Promedio"
            )
        
        # Calculate overall performance metrics
        avg_uptime = statistics.mean([d.uptime_percentage for d in device_metrics]) if device_metrics else 0
        avg_fps = statistics.mean([d.average_fps for d in device_metrics]) if device_metrics else 0
        total_violations = sum([d.violations_detected for d in device_metrics])
        
        # Build content
        content_sections = []
        
        content_sections.append(f"""
        <div class="section">
            <h2>Resumen de Rendimiento de Dispositivos</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">{len(device_metrics)}</span>
                    <span class="metric-label">Dispositivos Activos</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{avg_uptime:.1f}%</span>
                    <span class="metric-label">Uptime Promedio</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{avg_fps:.1f}</span>
                    <span class="metric-label">FPS Promedio</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{total_violations}</span>
                    <span class="metric-label">Total Violaciones</span>
                </div>
            </div>
        </div>
        """)
        
        # Device details table
        content_sections.append(f"""
        <div class="section">
            <h2>Detalles por Dispositivo</h2>
            <table>
                <thead>
                    <tr>
                        <th>Dispositivo</th>
                        <th>Uptime</th>
                        <th>FPS</th>
                        <th>Frames Procesados</th>
                        <th>Errores</th>
                        <th>Violaciones</th>
                        <th>Precisión</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([
                        f"<tr><td>{d.device_id}</td><td>{d.uptime_percentage:.1f}%</td><td>{d.average_fps:.1f}</td><td>{d.frames_processed:,}</td><td>{d.error_count}</td><td>{d.violations_detected}</td><td>{d.accuracy_score:.2f}</td></tr>"
                        for d in device_metrics
                    ])}
                </tbody>
            </table>
        </div>
        """)
        
        # Add charts
        if config.include_charts:
            for chart_name, chart_data in charts.items():
                content_sections.append(f"""
                <div class="section">
                    <div class="chart-container">
                        <img src="{chart_data}" class="chart" alt="{chart_name}">
                    </div>
                </div>
                """)
        
        html_content = self.templates['base'].format(
            title="Reporte de Rendimiento de Dispositivos",
            period=f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            content='\n'.join(content_sections)
        )
        
        return {
            "report_type": config.report_type.value,
            "period": f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            "device_metrics": [asdict(d) for d in device_metrics],
            "summary": {
                "total_devices": len(device_metrics),
                "average_uptime": avg_uptime,
                "average_fps": avg_fps,
                "total_violations": total_violations
            },
            "charts": charts if config.include_charts else {},
            "html_content": html_content,
            "generated_at": datetime.now().isoformat()
        }
    
    async def _generate_traffic_flow_report(self, config: ReportConfig) -> Dict[str, Any]:
        """Generate traffic flow analysis report."""
        traffic_metrics = self.analyzer.analyze_traffic_flow(
            config.start_date, config.end_date, config.device_ids
        )
        
        # Generate traffic flow charts
        charts = {}
        if config.include_charts:
            # Hourly traffic distribution
            charts['hourly_traffic'] = self.chart_generator.create_line_chart(
                {'Tráfico por Hora': [traffic_metrics.hourly_distribution.get(h, 0) for h in range(24)]},
                "Distribución Horaria del Tráfico",
                "Hora del Día", "Número de Detecciones"
            )
            
            # Vehicle types distribution
            charts['vehicle_types'] = self.chart_generator.create_pie_chart(
                traffic_metrics.vehicle_types,
                "Distribución de Tipos de Vehículos"
            )
        
        # Build content
        content_sections = []
        
        content_sections.append(f"""
        <div class="section">
            <h2>Análisis de Flujo de Tráfico</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <span class="metric-value">{traffic_metrics.total_vehicles}</span>
                    <span class="metric-label">Total Vehículos</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{traffic_metrics.average_speed:.1f}</span>
                    <span class="metric-label">Velocidad Promedio</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{traffic_metrics.peak_hour}:00</span>
                    <span class="metric-label">Hora Pico</span>
                </div>
                <div class="metric-card">
                    <span class="metric-value">{traffic_metrics.device_uptime:.1f}%</span>
                    <span class="metric-label">Uptime Dispositivos</span>
                </div>
            </div>
        </div>
        """)
        
        # Add charts
        if config.include_charts:
            for chart_name, chart_data in charts.items():
                content_sections.append(f"""
                <div class="section">
                    <div class="chart-container">
                        <img src="{chart_data}" class="chart" alt="{chart_name}">
                    </div>
                </div>
                """)
        
        html_content = self.templates['base'].format(
            title="Reporte de Flujo de Tráfico",
            period=f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            content='\n'.join(content_sections)
        )
        
        return {
            "report_type": config.report_type.value,
            "period": f"{config.start_date.strftime('%Y-%m-%d')} - {config.end_date.strftime('%Y-%m-%d')}",
            "traffic_metrics": asdict(traffic_metrics),
            "charts": charts if config.include_charts else {},
            "html_content": html_content,
            "generated_at": datetime.now().isoformat()
        }


class DashboardManager:
    """Manager for real-time dashboards."""
    
    def __init__(self, storage_service=None):
        self.storage_service = storage_service
        self.analyzer = TrafficDataAnalyzer(storage_service)
        
    def get_realtime_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for dashboard."""
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get today's data
        traffic_metrics = self.analyzer.analyze_traffic_flow(today_start, now)
        violation_summary = self.analyzer.analyze_violations(today_start, now)
        device_metrics = self.analyzer.analyze_device_performance(today_start, now)
        
        return {
            "timestamp": now.isoformat(),
            "today_vehicles": traffic_metrics.total_vehicles,
            "today_violations": violation_summary.total_violations,
            "active_devices": len(device_metrics),
            "average_speed": traffic_metrics.average_speed,
            "peak_hour": traffic_metrics.peak_hour,
            "violation_types": violation_summary.by_type,
            "device_status": [
                {
                    "device_id": d.device_id,
                    "status": "online" if d.uptime_percentage > 90 else "degraded",
                    "fps": d.average_fps,
                    "violations": d.violations_detected
                }
                for d in device_metrics
            ],
            "hourly_distribution": traffic_metrics.hourly_distribution
        }
    
    def get_dashboard_charts(self) -> Dict[str, str]:
        """Get dashboard charts data."""
        chart_gen = ChartGenerator("minimal")
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get data
        traffic_metrics = self.analyzer.analyze_traffic_flow(today_start, now)
        violation_summary = self.analyzer.analyze_violations(today_start, now)
        
        charts = {}
        
        # Real-time violation types
        charts['violation_types'] = chart_gen.create_plotly_interactive_chart({
            'values': violation_summary.by_type,
            'title': 'Tipos de Violaciones - Hoy'
        }, 'pie')
        
        # Hourly traffic
        charts['hourly_traffic'] = chart_gen.create_plotly_interactive_chart({
            'Tráfico': [traffic_metrics.hourly_distribution.get(h, 0) for h in range(24)],
            'title': 'Distribución Horaria del Tráfico',
            'x_label': 'Hora',
            'y_label': 'Detecciones'
        }, 'line')
        
        return charts