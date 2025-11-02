"""
Dashboard service for real-time traffic monitoring and visualization.

This module provides web-based dashboard functionality including:
- Real-time data streaming
- Interactive charts and graphs
- Live device monitoring
- Alert management
- Custom dashboard configurations
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
import json
from dataclasses import dataclass, asdict
from enum import Enum
import time

import websockets
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from .report_generator import (
    ReportGenerator, DashboardManager, ReportConfig, ReportType,
    TrafficDataAnalyzer
)


logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AlertType(Enum):
    """Types of alerts."""
    DEVICE_OFFLINE = "device_offline"
    HIGH_VIOLATION_RATE = "high_violation_rate"
    SYSTEM_ERROR = "system_error"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    STORAGE_CAPACITY = "storage_capacity"


@dataclass
class Alert:
    """Alert data structure."""
    alert_id: str
    alert_type: AlertType
    level: AlertLevel
    title: str
    message: str
    device_id: Optional[str]
    timestamp: datetime
    acknowledged: bool = False
    resolved: bool = False


@dataclass
class DashboardConfig:
    """Dashboard configuration."""
    refresh_interval: int = 5  # seconds
    chart_update_interval: int = 10  # seconds
    max_data_points: int = 100
    alert_retention_hours: int = 24
    auto_refresh: bool = True
    theme: str = "light"  # light, dark
    layout: str = "default"  # default, compact, detailed


class DashboardService:
    """Main dashboard service."""
    
    def __init__(self, storage_service=None, port: int = 8080):
        self.storage_service = storage_service
        self.port = port
        
        # Initialize components
        self.analyzer = TrafficDataAnalyzer(storage_service)
        self.dashboard_manager = DashboardManager(storage_service)
        self.report_generator = ReportGenerator(storage_service)
        
        # Active connections
        self.active_connections: Set[WebSocket] = set()
        
        # Alerts system
        self.alerts: List[Alert] = []
        self.alert_thresholds = {
            'max_violation_rate': 50,  # violations per hour
            'min_device_uptime': 90,   # percentage
            'max_response_time': 5000   # milliseconds
        }
        
        # Dashboard configuration
        self.config = DashboardConfig()
        
        # FastAPI app
        self.app = FastAPI(title="Traffic Analysis Dashboard")
        self._setup_routes()
        
        # Background tasks
        self._running = False
        self._background_tasks = []
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard_home():
            """Main dashboard page."""
            return self._render_dashboard()
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            """Get current dashboard metrics."""
            try:
                metrics = self.dashboard_manager.get_realtime_metrics()
                return JSONResponse(content=metrics)
            except Exception as e:
                logger.error(f"Error getting metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/charts")
        async def get_charts():
            """Get dashboard charts data."""
            try:
                charts = self.dashboard_manager.get_dashboard_charts()
                return JSONResponse(content=charts)
            except Exception as e:
                logger.error(f"Error getting charts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/alerts")
        async def get_alerts():
            """Get current alerts."""
            try:
                active_alerts = [asdict(alert) for alert in self.alerts if not alert.resolved]
                return JSONResponse(content={"alerts": active_alerts})
            except Exception as e:
                logger.error(f"Error getting alerts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/alerts/{alert_id}/acknowledge")
        async def acknowledge_alert(alert_id: str):
            """Acknowledge an alert."""
            try:
                for alert in self.alerts:
                    if alert.alert_id == alert_id:
                        alert.acknowledged = True
                        logger.info(f"Alert {alert_id} acknowledged")
                        await self._broadcast_alerts()
                        return JSONResponse(content={"status": "acknowledged"})
                
                raise HTTPException(status_code=404, detail="Alert not found")
            except Exception as e:
                logger.error(f"Error acknowledging alert: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/api/alerts/{alert_id}/resolve")
        async def resolve_alert(alert_id: str):
            """Resolve an alert."""
            try:
                for alert in self.alerts:
                    if alert.alert_id == alert_id:
                        alert.resolved = True
                        logger.info(f"Alert {alert_id} resolved")
                        await self._broadcast_alerts()
                        return JSONResponse(content={"status": "resolved"})
                
                raise HTTPException(status_code=404, detail="Alert not found")
            except Exception as e:
                logger.error(f"Error resolving alert: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/reports/generate/{report_type}")
        async def generate_report(
            report_type: str,
            start_date: str,
            end_date: str,
            device_ids: str = "",
            background_tasks: BackgroundTasks = None
        ):
            """Generate and return a report."""
            try:
                from datetime import datetime
                
                # Parse parameters
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                devices = device_ids.split(',') if device_ids else None
                
                # Create report config
                report_config = ReportConfig(
                    report_type=ReportType(report_type),
                    start_date=start_dt,
                    end_date=end_dt,
                    device_ids=devices,
                    include_charts=True,
                    output_format="html"
                )
                
                # Generate report
                report = await self.report_generator.generate_report(report_config)
                
                return JSONResponse(content=report)
                
            except Exception as e:
                logger.error(f"Error generating report: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await websocket.accept()
            self.active_connections.add(websocket)
            
            try:
                while True:
                    # Keep connection alive and handle incoming messages
                    data = await websocket.receive_text()
                    logger.debug(f"Received WebSocket message: {data}")
                    
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
                logger.info("WebSocket connection closed")
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                self.active_connections.discard(websocket)
    
    def _render_dashboard(self) -> str:
        """Render the main dashboard HTML."""
        return """
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Dashboard de Análisis de Tráfico</title>
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }
                
                body {
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    color: #333;
                }
                
                .dashboard-container {
                    max-width: 1400px;
                    margin: 0 auto;
                    padding: 20px;
                }
                
                .header {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 20px;
                    border-radius: 15px;
                    margin-bottom: 20px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    backdrop-filter: blur(10px);
                }
                
                .header h1 {
                    color: #2E86AB;
                    font-size: 2.5em;
                    text-align: center;
                    margin-bottom: 10px;
                }
                
                .header .subtitle {
                    text-align: center;
                    color: #666;
                    font-size: 1.1em;
                }
                
                .metrics-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .metric-card {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 25px;
                    border-radius: 15px;
                    text-align: center;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    backdrop-filter: blur(10px);
                    transition: transform 0.3s ease;
                }
                
                .metric-card:hover {
                    transform: translateY(-5px);
                }
                
                .metric-value {
                    font-size: 3em;
                    font-weight: bold;
                    color: #2E86AB;
                    display: block;
                    margin-bottom: 10px;
                }
                
                .metric-label {
                    font-size: 1.1em;
                    color: #666;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .charts-section {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }
                
                .chart-container {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    backdrop-filter: blur(10px);
                }
                
                .chart-title {
                    font-size: 1.3em;
                    font-weight: bold;
                    color: #333;
                    margin-bottom: 20px;
                    text-align: center;
                }
                
                .alerts-panel {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 25px;
                    border-radius: 15px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    backdrop-filter: blur(10px);
                    margin-bottom: 20px;
                }
                
                .alert-item {
                    padding: 15px;
                    margin: 10px 0;
                    border-radius: 8px;
                    border-left: 4px solid;
                }
                
                .alert-warning {
                    background-color: #fff3cd;
                    border-color: #ffecb5;
                    color: #856404;
                }
                
                .alert-error {
                    background-color: #f8d7da;
                    border-color: #f5c6cb;
                    color: #721c24;
                }
                
                .alert-info {
                    background-color: #d1ecf1;
                    border-color: #bee5eb;
                    color: #0c5460;
                }
                
                .controls-panel {
                    background: rgba(255, 255, 255, 0.95);
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
                    backdrop-filter: blur(10px);
                    text-align: center;
                }
                
                .btn {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    cursor: pointer;
                    font-size: 1em;
                    margin: 5px;
                    transition: all 0.3s ease;
                }
                
                .btn:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                }
                
                .status-indicator {
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    border-radius: 50%;
                    margin-right: 8px;
                }
                
                .status-online {
                    background-color: #28a745;
                }
                
                .status-offline {
                    background-color: #dc3545;
                }
                
                .status-degraded {
                    background-color: #ffc107;
                }
                
                .last-updated {
                    text-align: center;
                    color: #666;
                    font-size: 0.9em;
                    margin-top: 20px;
                }
            </style>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        </head>
        <body>
            <div class="dashboard-container">
                <div class="header">
                    <h1>🚗 Dashboard de Análisis de Tráfico</h1>
                    <p class="subtitle">Monitoreo en Tiempo Real del Sistema de Detección de Violaciones</p>
                </div>
                
                <div class="metrics-grid" id="metrics-grid">
                    <!-- Metrics will be loaded here -->
                </div>
                
                <div class="alerts-panel">
                    <h2>🚨 Alertas del Sistema</h2>
                    <div id="alerts-container">
                        <!-- Alerts will be loaded here -->
                    </div>
                </div>
                
                <div class="charts-section">
                    <div class="chart-container">
                        <div class="chart-title">Violaciones por Tipo</div>
                        <div id="violation-types-chart"></div>
                    </div>
                    
                    <div class="chart-container">
                        <div class="chart-title">Distribución Horaria del Tráfico</div>
                        <div id="hourly-traffic-chart"></div>
                    </div>
                </div>
                
                <div class="controls-panel">
                    <h3>Controles del Dashboard</h3>
                    <button class="btn" onclick="refreshData()">🔄 Actualizar Datos</button>
                    <button class="btn" onclick="toggleAutoRefresh()">⏱️ Auto-Actualización</button>
                    <button class="btn" onclick="generateReport()">📊 Generar Reporte</button>
                    <button class="btn" onclick="exportData()">💾 Exportar Datos</button>
                </div>
                
                <div class="last-updated" id="last-updated">
                    Última actualización: --
                </div>
            </div>
            
            <script>
                let autoRefresh = true;
                let refreshInterval;
                let ws;
                
                // Initialize WebSocket connection
                function initWebSocket() {
                    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                    const wsUrl = `${protocol}//${window.location.host}/ws`;
                    
                    ws = new WebSocket(wsUrl);
                    
                    ws.onopen = function(event) {
                        console.log('WebSocket connected');
                    };
                    
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        if (data.type === 'metrics_update') {
                            updateMetrics(data.data);
                        } else if (data.type === 'alerts_update') {
                            updateAlerts(data.data);
                        }
                    };
                    
                    ws.onclose = function(event) {
                        console.log('WebSocket disconnected, attempting to reconnect...');
                        setTimeout(initWebSocket, 5000);
                    };
                    
                    ws.onerror = function(error) {
                        console.error('WebSocket error:', error);
                    };
                }
                
                // Load dashboard data
                async function loadDashboardData() {
                    try {
                        // Load metrics
                        const metricsResponse = await fetch('/api/metrics');
                        const metrics = await metricsResponse.json();
                        updateMetrics(metrics);
                        
                        // Load alerts
                        const alertsResponse = await fetch('/api/alerts');
                        const alerts = await alertsResponse.json();
                        updateAlerts(alerts.alerts);
                        
                        // Load charts
                        const chartsResponse = await fetch('/api/charts');
                        const charts = await chartsResponse.json();
                        updateCharts(charts);
                        
                        document.getElementById('last-updated').textContent = 
                            'Última actualización: ' + new Date().toLocaleString();
                            
                    } catch (error) {
                        console.error('Error loading dashboard data:', error);
                    }
                }
                
                // Update metrics display
                function updateMetrics(metrics) {
                    const metricsGrid = document.getElementById('metrics-grid');
                    metricsGrid.innerHTML = `
                        <div class="metric-card">
                            <span class="metric-value">${metrics.today_vehicles || 0}</span>
                            <span class="metric-label">Vehículos Hoy</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-value">${metrics.today_violations || 0}</span>
                            <span class="metric-label">Violaciones Hoy</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-value">${metrics.active_devices || 0}</span>
                            <span class="metric-label">Dispositivos Activos</span>
                        </div>
                        <div class="metric-card">
                            <span class="metric-value">${(metrics.average_speed || 0).toFixed(1)}</span>
                            <span class="metric-label">Velocidad Promedio (km/h)</span>
                        </div>
                    `;
                }
                
                // Update alerts display
                function updateAlerts(alerts) {
                    const alertsContainer = document.getElementById('alerts-container');
                    
                    if (!alerts || alerts.length === 0) {
                        alertsContainer.innerHTML = '<p>✅ No hay alertas activas</p>';
                        return;
                    }
                    
                    const alertsHtml = alerts.map(alert => {
                        const alertClass = `alert-${alert.level}`;
                        return `
                            <div class="alert-item ${alertClass}">
                                <strong>${alert.title}</strong><br>
                                ${alert.message}<br>
                                <small>${new Date(alert.timestamp).toLocaleString()}</small>
                                ${!alert.acknowledged ? 
                                    `<button class="btn" onclick="acknowledgeAlert('${alert.alert_id}')">Reconocer</button>` : 
                                    ''
                                }
                            </div>
                        `;
                    }).join('');
                    
                    alertsContainer.innerHTML = alertsHtml;
                }
                
                // Update charts
                function updateCharts(charts) {
                    // Update violation types chart
                    if (charts.violation_types) {
                        const violationData = JSON.parse(charts.violation_types);
                        Plotly.newPlot('violation-types-chart', violationData.data, violationData.layout);
                    }
                    
                    // Update hourly traffic chart
                    if (charts.hourly_traffic) {
                        const trafficData = JSON.parse(charts.hourly_traffic);
                        Plotly.newPlot('hourly-traffic-chart', trafficData.data, trafficData.layout);
                    }
                }
                
                // Control functions
                function refreshData() {
                    loadDashboardData();
                }
                
                function toggleAutoRefresh() {
                    autoRefresh = !autoRefresh;
                    if (autoRefresh) {
                        startAutoRefresh();
                    } else {
                        clearInterval(refreshInterval);
                    }
                }
                
                function startAutoRefresh() {
                    refreshInterval = setInterval(loadDashboardData, 5000);
                }
                
                async function acknowledgeAlert(alertId) {
                    try {
                        await fetch(`/api/alerts/${alertId}/acknowledge`, { method: 'POST' });
                        loadDashboardData();
                    } catch (error) {
                        console.error('Error acknowledging alert:', error);
                    }
                }
                
                async function generateReport() {
                    const now = new Date();
                    const yesterday = new Date(now.getTime() - 24 * 60 * 60 * 1000);
                    
                    try {
                        const response = await fetch(
                            `/api/reports/generate/daily_summary?start_date=${yesterday.toISOString()}&end_date=${now.toISOString()}`
                        );
                        const report = await response.json();
                        
                        // Open report in new window
                        const newWindow = window.open();
                        newWindow.document.write(report.html_content);
                        newWindow.document.close();
                        
                    } catch (error) {
                        console.error('Error generating report:', error);
                        alert('Error al generar el reporte');
                    }
                }
                
                function exportData() {
                    // Implement data export functionality
                    alert('Funcionalidad de exportación próximamente disponible');
                }
                
                // Initialize dashboard
                document.addEventListener('DOMContentLoaded', function() {
                    initWebSocket();
                    loadDashboardData();
                    
                    if (autoRefresh) {
                        startAutoRefresh();
                    }
                });
            </script>
        </body>
        </html>
        """
    
    async def start(self):
        """Start the dashboard service."""
        logger.info(f"Starting dashboard service on port {self.port}")
        self._running = True
        
        # Start background tasks
        self._background_tasks = [
            asyncio.create_task(self._metrics_updater()),
            asyncio.create_task(self._alert_monitor()),
            asyncio.create_task(self._cleanup_old_alerts())
        ]
        
        # Start the web server
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        try:
            await server.serve()
        except Exception as e:
            logger.error(f"Dashboard service error: {e}")
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the dashboard service."""
        logger.info("Stopping dashboard service")
        self._running = False
        
        # Cancel background tasks
        for task in self._background_tasks:
            task.cancel()
        
        # Close WebSocket connections
        for connection in self.active_connections.copy():
            await connection.close()
        
    async def _metrics_updater(self):
        """Background task to update metrics."""
        while self._running:
            try:
                metrics = self.dashboard_manager.get_realtime_metrics()
                await self._broadcast_message({
                    "type": "metrics_update",
                    "data": metrics
                })
                
                await asyncio.sleep(self.config.refresh_interval)
                
            except Exception as e:
                logger.error(f"Error updating metrics: {e}")
                await asyncio.sleep(5)
    
    async def _alert_monitor(self):
        """Background task to monitor for alerts."""
        while self._running:
            try:
                await self._check_alerts()
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error monitoring alerts: {e}")
                await asyncio.sleep(10)
    
    async def _check_alerts(self):
        """Check for new alerts."""
        now = datetime.now()
        
        # Get current metrics
        metrics = self.dashboard_manager.get_realtime_metrics()
        
        # Check violation rate
        if metrics['today_violations'] > self.alert_thresholds['max_violation_rate']:
            alert_id = f"high_violations_{int(now.timestamp())}"
            if not any(a.alert_id == alert_id for a in self.alerts):
                alert = Alert(
                    alert_id=alert_id,
                    alert_type=AlertType.HIGH_VIOLATION_RATE,
                    level=AlertLevel.WARNING,
                    title="Alta tasa de violaciones",
                    message=f"Se han detectado {metrics['today_violations']} violaciones hoy",
                    device_id=None,
                    timestamp=now
                )
                self.alerts.append(alert)
                logger.warning(f"High violation rate alert: {metrics['today_violations']}")
        
        # Check device status
        for device in metrics.get('device_status', []):
            if device['status'] != 'online':
                alert_id = f"device_offline_{device['device_id']}_{int(now.timestamp())}"
                if not any(a.alert_id == alert_id for a in self.alerts):
                    alert = Alert(
                        alert_id=alert_id,
                        alert_type=AlertType.DEVICE_OFFLINE,
                        level=AlertLevel.ERROR,
                        title=f"Dispositivo {device['device_id']} desconectado",
                        message=f"El dispositivo {device['device_id']} está {device['status']}",
                        device_id=device['device_id'],
                        timestamp=now
                    )
                    self.alerts.append(alert)
                    logger.error(f"Device offline alert: {device['device_id']}")
        
        # Broadcast alerts update
        await self._broadcast_alerts()
    
    async def _cleanup_old_alerts(self):
        """Clean up old resolved alerts."""
        while self._running:
            try:
                cutoff_time = datetime.now() - timedelta(hours=self.config.alert_retention_hours)
                
                # Remove old resolved alerts
                old_count = len(self.alerts)
                self.alerts = [
                    alert for alert in self.alerts
                    if not (alert.resolved and alert.timestamp < cutoff_time)
                ]
                
                removed_count = old_count - len(self.alerts)
                if removed_count > 0:
                    logger.info(f"Cleaned up {removed_count} old alerts")
                
                await asyncio.sleep(3600)  # Clean up every hour
                
            except Exception as e:
                logger.error(f"Error cleaning up alerts: {e}")
                await asyncio.sleep(300)
    
    async def _broadcast_message(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients."""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.warning(f"Failed to send message to client: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        self.active_connections -= disconnected
    
    async def _broadcast_alerts(self):
        """Broadcast alerts update."""
        active_alerts = [asdict(alert) for alert in self.alerts if not alert.resolved]
        await self._broadcast_message({
            "type": "alerts_update",
            "data": active_alerts
        })


class DashboardCLI:
    """Command-line interface for dashboard management."""
    
    def __init__(self, storage_service=None):
        self.storage_service = storage_service
        self.dashboard_service = DashboardService(storage_service)
    
    async def start_dashboard(self, port: int = 8080):
        """Start the dashboard web server."""
        self.dashboard_service.port = port
        await self.dashboard_service.start()
    
    async def generate_test_report(self, report_type: str = "daily_summary"):
        """Generate a test report."""
        from datetime import datetime, timedelta
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        config = ReportConfig(
            report_type=ReportType(report_type),
            start_date=start_date,
            end_date=end_date,
            include_charts=True,
            output_format="html"
        )
        
        report_generator = ReportGenerator(self.storage_service)
        report = await report_generator.generate_report(config)
        
        # Save report to file
        output_file = f"test_report_{report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report['html_content'])
        
        print(f"Test report generated: {output_file}")
        return output_file
    
    async def test_dashboard_metrics(self):
        """Test dashboard metrics generation."""
        dashboard_manager = DashboardManager(self.storage_service)
        
        print("Testing dashboard metrics...")
        metrics = dashboard_manager.get_realtime_metrics()
        
        print(f"Today's vehicles: {metrics['today_vehicles']}")
        print(f"Today's violations: {metrics['today_violations']}")
        print(f"Active devices: {metrics['active_devices']}")
        print(f"Average speed: {metrics['average_speed']:.1f} km/h")
        
        return metrics


if __name__ == "__main__":
    import sys
    
    async def main():
        cli = DashboardCLI()
        
        if len(sys.argv) > 1:
            command = sys.argv[1]
            
            if command == "start":
                port = int(sys.argv[2]) if len(sys.argv) > 2 else 8080
                await cli.start_dashboard(port)
            
            elif command == "test-report":
                report_type = sys.argv[2] if len(sys.argv) > 2 else "daily_summary"
                await cli.generate_test_report(report_type)
            
            elif command == "test-metrics":
                await cli.test_dashboard_metrics()
            
            else:
                print("Usage: python dashboard_service.py [start|test-report|test-metrics] [args]")
        
        else:
            # Default: start dashboard
            await cli.start_dashboard()
    
    asyncio.run(main())