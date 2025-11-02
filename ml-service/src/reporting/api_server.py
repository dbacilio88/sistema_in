"""
API server for reporting and dashboard services.

This module provides REST API endpoints for:
- Report generation and management
- Dashboard data access
- Chart generation
- Data export utilities
- Real-time metrics
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
import uuid
from dataclasses import asdict

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Path as FastAPIPath
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .report_generator import (
    ReportGenerator, ReportConfig, ReportType, DashboardManager
)
from .dashboard_service import DashboardService, Alert, AlertType, AlertLevel
from .visualization_utils import AdvancedChartGenerator, ChartConfig, VisualizationTheme


logger = logging.getLogger(__name__)


# Pydantic models for request/response
class ReportRequest(BaseModel):
    """Request model for report generation."""
    report_type: str = Field(..., description="Type of report to generate")
    start_date: str = Field(..., description="Start date in ISO format")
    end_date: str = Field(..., description="End date in ISO format")
    device_ids: Optional[List[str]] = Field(None, description="List of device IDs to include")
    violation_types: Optional[List[str]] = Field(None, description="List of violation types to include")
    include_charts: bool = Field(True, description="Whether to include charts")
    include_raw_data: bool = Field(False, description="Whether to include raw data")
    output_format: str = Field("html", description="Output format (html, pdf, json)")
    chart_style: str = Field("default", description="Chart style theme")
    language: str = Field("es", description="Report language")


class ChartRequest(BaseModel):
    """Request model for chart generation."""
    chart_type: str = Field(..., description="Type of chart to generate")
    data: Dict[str, Any] = Field(..., description="Chart data")
    title: str = Field("Chart", description="Chart title")
    theme: str = Field("default", description="Chart theme")
    width: int = Field(800, description="Chart width")
    height: int = Field(600, description="Chart height")
    interactive: bool = Field(False, description="Whether chart should be interactive")


class MetricsResponse(BaseModel):
    """Response model for metrics."""
    timestamp: str
    today_vehicles: int
    today_violations: int
    active_devices: int
    average_speed: float
    peak_hour: int
    violation_types: Dict[str, int]
    device_status: List[Dict[str, Any]]
    hourly_distribution: Dict[str, int]


class ReportResponse(BaseModel):
    """Response model for generated reports."""
    report_id: str
    report_type: str
    period: str
    generated_at: str
    status: str
    download_url: Optional[str] = None
    preview_url: Optional[str] = None
    metadata: Dict[str, Any]


class ReportingAPIServer:
    """FastAPI server for reporting and dashboard services."""
    
    def __init__(self, storage_service=None, port: int = 8081):
        self.storage_service = storage_service
        self.port = port
        
        # Initialize services
        self.report_generator = ReportGenerator(storage_service)
        self.dashboard_manager = DashboardManager(storage_service)
        self.chart_generator = AdvancedChartGenerator()
        
        # Report storage
        self.generated_reports: Dict[str, Dict[str, Any]] = {}
        
        # FastAPI app
        self.app = FastAPI(
            title="Traffic Analysis Reporting API",
            description="API for traffic analysis reports and dashboards",
            version="1.0.0"
        )
        
        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def api_home():
            """API documentation home page."""
            return """
            <html>
                <head><title>Traffic Analysis Reporting API</title></head>
                <body>
                    <h1>Traffic Analysis Reporting API</h1>
                    <p>API para generación de reportes y dashboards del sistema de análisis de tráfico.</p>
                    <h2>Endpoints Principales:</h2>
                    <ul>
                        <li><a href="/docs">Documentación Interactiva (Swagger)</a></li>
                        <li><a href="/redoc">Documentación ReDoc</a></li>
                        <li><a href="/api/v1/metrics">Métricas en Tiempo Real</a></li>
                        <li><a href="/api/v1/reports">Lista de Reportes</a></li>
                    </ul>
                </body>
            </html>
            """
        
        # Metrics endpoints
        @self.app.get("/api/v1/metrics", response_model=MetricsResponse)
        async def get_realtime_metrics():
            """Get real-time dashboard metrics."""
            try:
                metrics = self.dashboard_manager.get_realtime_metrics()
                return MetricsResponse(**metrics)
            except Exception as e:
                logger.error(f"Error getting metrics: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/metrics/history")
        async def get_metrics_history(
            start_date: str = Query(..., description="Start date in ISO format"),
            end_date: str = Query(..., description="End date in ISO format"),
            interval: str = Query("hour", description="Data interval (hour, day)")
        ):
            """Get historical metrics data."""
            try:
                # Parse dates
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                
                # Generate historical data (simplified for demo)
                history = []
                current = start_dt
                delta = timedelta(hours=1) if interval == "hour" else timedelta(days=1)
                
                while current <= end_dt:
                    # Simulate metrics for each time point
                    hour_metrics = {
                        "timestamp": current.isoformat(),
                        "vehicles": 10 + (hash(str(current)) % 50),
                        "violations": hash(str(current)) % 20,
                        "average_speed": 45 + (hash(str(current)) % 20)
                    }
                    history.append(hour_metrics)
                    current += delta
                
                return {"history": history, "interval": interval}
                
            except Exception as e:
                logger.error(f"Error getting metrics history: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Report generation endpoints
        @self.app.post("/api/v1/reports/generate", response_model=ReportResponse)
        async def generate_report(
            request: ReportRequest,
            background_tasks: BackgroundTasks
        ):
            """Generate a new report."""
            try:
                # Create report ID
                report_id = str(uuid.uuid4())
                
                # Parse dates
                start_dt = datetime.fromisoformat(request.start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(request.end_date.replace('Z', '+00:00'))
                
                # Create report config
                report_config = ReportConfig(
                    report_type=ReportType(request.report_type),
                    start_date=start_dt,
                    end_date=end_dt,
                    device_ids=request.device_ids,
                    violation_types=request.violation_types,
                    include_charts=request.include_charts,
                    include_raw_data=request.include_raw_data,
                    output_format=request.output_format,
                    chart_style=request.chart_style,
                    language=request.language
                )
                
                # Store report info
                self.generated_reports[report_id] = {
                    "id": report_id,
                    "config": asdict(report_config),
                    "status": "generating",
                    "created_at": datetime.now().isoformat(),
                    "report_data": None
                }
                
                # Generate report in background
                background_tasks.add_task(
                    self._generate_report_background,
                    report_id,
                    report_config
                )
                
                return ReportResponse(
                    report_id=report_id,
                    report_type=request.report_type,
                    period=f"{request.start_date} - {request.end_date}",
                    generated_at=datetime.now().isoformat(),
                    status="generating",
                    metadata={"config": asdict(report_config)}
                )
                
            except Exception as e:
                logger.error(f"Error generating report: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/reports", response_model=List[ReportResponse])
        async def list_reports(
            limit: int = Query(10, description="Maximum number of reports to return"),
            offset: int = Query(0, description="Number of reports to skip")
        ):
            """List generated reports."""
            try:
                reports = list(self.generated_reports.values())
                
                # Sort by creation date (newest first)
                reports.sort(key=lambda r: r["created_at"], reverse=True)
                
                # Apply pagination
                paginated_reports = reports[offset:offset+limit]
                
                response = []
                for report in paginated_reports:
                    config = report["config"]
                    response.append(ReportResponse(
                        report_id=report["id"],
                        report_type=config["report_type"],
                        period=f"{config['start_date']} - {config['end_date']}",
                        generated_at=report["created_at"],
                        status=report["status"],
                        download_url=f"/api/v1/reports/{report['id']}/download" if report["status"] == "completed" else None,
                        preview_url=f"/api/v1/reports/{report['id']}/preview" if report["status"] == "completed" else None,
                        metadata={"config": config}
                    ))
                
                return response
                
            except Exception as e:
                logger.error(f"Error listing reports: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/reports/{report_id}")
        async def get_report(report_id: str = FastAPIPath(..., description="Report ID")):
            """Get report details."""
            try:
                if report_id not in self.generated_reports:
                    raise HTTPException(status_code=404, detail="Report not found")
                
                report = self.generated_reports[report_id]
                config = report["config"]
                
                return ReportResponse(
                    report_id=report_id,
                    report_type=config["report_type"],
                    period=f"{config['start_date']} - {config['end_date']}",
                    generated_at=report["created_at"],
                    status=report["status"],
                    download_url=f"/api/v1/reports/{report_id}/download" if report["status"] == "completed" else None,
                    preview_url=f"/api/v1/reports/{report_id}/preview" if report["status"] == "completed" else None,
                    metadata={"config": config, "report_data": report.get("report_data")}
                )
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error getting report: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/reports/{report_id}/download")
        async def download_report(report_id: str = FastAPIPath(..., description="Report ID")):
            """Download generated report."""
            try:
                if report_id not in self.generated_reports:
                    raise HTTPException(status_code=404, detail="Report not found")
                
                report = self.generated_reports[report_id]
                
                if report["status"] != "completed":
                    raise HTTPException(status_code=400, detail="Report not ready for download")
                
                report_data = report.get("report_data")
                if not report_data:
                    raise HTTPException(status_code=404, detail="Report data not found")
                
                # Return JSON response with report data
                return JSONResponse(content=report_data)
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error downloading report: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/reports/{report_id}/preview", response_class=HTMLResponse)
        async def preview_report(report_id: str = FastAPIPath(..., description="Report ID")):
            """Preview generated report in HTML format."""
            try:
                if report_id not in self.generated_reports:
                    raise HTTPException(status_code=404, detail="Report not found")
                
                report = self.generated_reports[report_id]
                
                if report["status"] != "completed":
                    return "<html><body><h1>Report is still being generated...</h1></body></html>"
                
                report_data = report.get("report_data")
                if not report_data or "html_content" not in report_data:
                    return "<html><body><h1>Report preview not available</h1></body></html>"
                
                return report_data["html_content"]
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error previewing report: {e}")
                return "<html><body><h1>Error loading report preview</h1></body></html>"
        
        @self.app.delete("/api/v1/reports/{report_id}")
        async def delete_report(report_id: str = FastAPIPath(..., description="Report ID")):
            """Delete a generated report."""
            try:
                if report_id not in self.generated_reports:
                    raise HTTPException(status_code=404, detail="Report not found")
                
                del self.generated_reports[report_id]
                logger.info(f"Report {report_id} deleted")
                
                return {"message": "Report deleted successfully"}
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error deleting report: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Chart generation endpoints
        @self.app.post("/api/v1/charts/generate")
        async def generate_chart(request: ChartRequest):
            """Generate a custom chart."""
            try:
                # Create chart config
                chart_config = ChartConfig(
                    theme=VisualizationTheme(request.theme),
                    width=request.width,
                    height=request.height,
                    interactive=request.interactive
                )
                
                # Create chart generator
                chart_gen = AdvancedChartGenerator(chart_config)
                
                # Generate chart based on type
                if request.chart_type == "heatmap":
                    chart_data = chart_gen.create_violation_heatmap(
                        request.data, request.title
                    )
                elif request.chart_type == "timeline":
                    chart_data = chart_gen.create_violation_timeline(
                        request.data.get("violations", []), request.title
                    )
                elif request.chart_type == "speed_distribution":
                    chart_data = chart_gen.create_speed_distribution(
                        request.data.get("speeds", []), request.title
                    )
                elif request.chart_type == "performance_dashboard":
                    chart_data = chart_gen.create_performance_dashboard(
                        request.data.get("devices", [])
                    )
                else:
                    raise HTTPException(status_code=400, detail=f"Unsupported chart type: {request.chart_type}")
                
                return {
                    "chart_type": request.chart_type,
                    "title": request.title,
                    "chart_data": chart_data,
                    "config": asdict(chart_config),
                    "generated_at": datetime.now().isoformat()
                }
                
            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Error generating chart: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/charts/templates")
        async def get_chart_templates():
            """Get available chart templates."""
            from .visualization_utils import CHART_TEMPLATES
            
            return {
                "templates": CHART_TEMPLATES,
                "chart_types": [
                    "heatmap",
                    "timeline", 
                    "speed_distribution",
                    "performance_dashboard",
                    "trend_analysis",
                    "geographic_heatmap"
                ],
                "themes": [theme.value for theme in VisualizationTheme]
            }
        
        # Dashboard data endpoints
        @self.app.get("/api/v1/dashboard/charts")
        async def get_dashboard_charts():
            """Get charts for dashboard display."""
            try:
                charts = self.dashboard_manager.get_dashboard_charts()
                return {"charts": charts, "generated_at": datetime.now().isoformat()}
            except Exception as e:
                logger.error(f"Error getting dashboard charts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/api/v1/dashboard/alerts")
        async def get_dashboard_alerts():
            """Get current dashboard alerts."""
            try:
                # For now, return simulated alerts
                alerts = [
                    {
                        "alert_id": "alert_001",
                        "alert_type": "high_violation_rate",
                        "level": "warning",
                        "title": "Alta tasa de violaciones",
                        "message": "Se han detectado 45 violaciones en la última hora",
                        "device_id": None,
                        "timestamp": datetime.now().isoformat(),
                        "acknowledged": False,
                        "resolved": False
                    }
                ]
                
                return {"alerts": alerts}
            except Exception as e:
                logger.error(f"Error getting dashboard alerts: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Data export endpoints
        @self.app.get("/api/v1/export/violations")
        async def export_violations(
            start_date: str = Query(..., description="Start date in ISO format"),
            end_date: str = Query(..., description="End date in ISO format"),
            format: str = Query("csv", description="Export format (csv, json, excel)"),
            device_ids: Optional[str] = Query(None, description="Comma-separated device IDs")
        ):
            """Export violation data."""
            try:
                # Parse parameters
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                devices = device_ids.split(',') if device_ids else None
                
                # Get violation data (simplified for demo)
                violations = [
                    {
                        "violation_id": f"V{i:06d}",
                        "timestamp": (start_dt + timedelta(hours=i)).isoformat(),
                        "device_id": f"cam_{(i % 3) + 1:03d}",
                        "violation_type": ["speed", "red_light", "lane_violation"][i % 3],
                        "vehicle_class": ["car", "truck", "motorcycle"][i % 3],
                        "speed_kmh": 60 + (i % 30),
                        "confidence": 0.8 + (i % 20) / 100
                    }
                    for i in range(min(100, int((end_dt - start_dt).total_seconds() / 3600)))
                ]
                
                # Filter by devices if specified
                if devices:
                    violations = [v for v in violations if v["device_id"] in devices]
                
                if format == "csv":
                    import pandas as pd
                    df = pd.DataFrame(violations)
                    csv_data = df.to_csv(index=False)
                    
                    return JSONResponse(
                        content={"data": csv_data, "format": "csv"},
                        headers={"Content-Type": "application/json"}
                    )
                
                elif format == "excel":
                    return {"message": "Excel export not implemented yet", "data": violations}
                
                else:  # JSON
                    return {
                        "violations": violations,
                        "count": len(violations),
                        "period": f"{start_date} - {end_date}",
                        "exported_at": datetime.now().isoformat()
                    }
                
            except Exception as e:
                logger.error(f"Error exporting violations: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Health check endpoint
        @self.app.get("/api/v1/health")
        async def health_check():
            """API health check."""
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "services": {
                    "report_generator": "available",
                    "dashboard_manager": "available",
                    "chart_generator": "available"
                }
            }
    
    async def _generate_report_background(self, report_id: str, config: ReportConfig):
        """Generate report in background task."""
        try:
            # Update status
            if report_id in self.generated_reports:
                self.generated_reports[report_id]["status"] = "generating"
            
            # Generate report
            report_data = await self.report_generator.generate_report(config)
            
            # Store result
            if report_id in self.generated_reports:
                self.generated_reports[report_id]["status"] = "completed"
                self.generated_reports[report_id]["report_data"] = report_data
                self.generated_reports[report_id]["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Report {report_id} generated successfully")
            
        except Exception as e:
            logger.error(f"Error generating report {report_id}: {e}")
            
            if report_id in self.generated_reports:
                self.generated_reports[report_id]["status"] = "failed"
                self.generated_reports[report_id]["error"] = str(e)
    
    async def start(self):
        """Start the API server."""
        logger.info(f"Starting reporting API server on port {self.port}")
        
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
            logger.error(f"API server error: {e}")


if __name__ == "__main__":
    import sys
    
    async def main():
        port = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
        
        api_server = ReportingAPIServer(port=port)
        await api_server.start()
    
    asyncio.run(main())