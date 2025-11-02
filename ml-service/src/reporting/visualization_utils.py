"""
Data visualization utilities for traffic analysis reports.

This module provides advanced visualization components including:
- Interactive charts and graphs
- Custom plot styling
- Data export utilities
- Chart templates
- Animation capabilities
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any, Tuple
from pathlib import Path
import json
from dataclasses import dataclass
from enum import Enum
import base64
import io

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.animation as animation
from matplotlib.backends.backend_agg import FigureCanvasAgg
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.utils
import plotly.offline as pyo


logger = logging.getLogger(__name__)


class VisualizationTheme(Enum):
    """Visualization theme options."""
    DEFAULT = "default"
    DARK = "dark"
    MINIMAL = "minimal"
    PROFESSIONAL = "professional"
    COLORFUL = "colorful"


@dataclass
class ChartConfig:
    """Configuration for chart generation."""
    theme: VisualizationTheme = VisualizationTheme.DEFAULT
    width: int = 800
    height: int = 600
    dpi: int = 150
    interactive: bool = False
    animation: bool = False
    export_format: str = "png"  # png, svg, pdf, html


class AdvancedChartGenerator:
    """Advanced chart generator with multiple visualization libraries."""
    
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()
        self._setup_theme()
    
    def _setup_theme(self):
        """Setup visualization theme."""
        if self.config.theme == VisualizationTheme.DARK:
            plt.style.use('dark_background')
            self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE']
            self.bg_color = '#2C3E50'
            self.text_color = '#ECF0F1'
        elif self.config.theme == VisualizationTheme.MINIMAL:
            plt.style.use('seaborn-v0_8-whitegrid')
            self.colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#593E40']
            self.bg_color = '#FFFFFF'
            self.text_color = '#2C3E50'
        elif self.config.theme == VisualizationTheme.PROFESSIONAL:
            plt.style.use('seaborn-v0_8-paper')
            self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
            self.bg_color = '#FAFAFA'
            self.text_color = '#333333'
        elif self.config.theme == VisualizationTheme.COLORFUL:
            plt.style.use('seaborn-v0_8-bright')
            self.colors = ['#FF5733', '#33FF57', '#3357FF', '#FF33F1', '#F1FF33', '#33F1FF', '#F133FF']
            self.bg_color = '#F8F9FA'
            self.text_color = '#212529'
        else:  # DEFAULT
            plt.style.use('default')
            self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
            self.bg_color = '#FFFFFF'
            self.text_color = '#000000'
    
    def create_violation_heatmap(self, data: Dict[str, Dict[str, int]], 
                               title: str = "Mapa de Calor de Violaciones") -> str:
        """Create advanced violation heatmap."""
        # Convert data to matrix format
        devices = list(data.keys())
        hours = list(range(24))
        
        matrix = []
        for device in devices:
            device_data = data.get(device, {})
            row = [device_data.get(str(hour), 0) for hour in hours]
            matrix.append(row)
        
        if self.config.interactive:
            return self._create_plotly_heatmap(matrix, devices, hours, title)
        else:
            return self._create_matplotlib_heatmap(matrix, devices, hours, title)
    
    def _create_plotly_heatmap(self, matrix: List[List[int]], 
                              devices: List[str], hours: List[int], title: str) -> str:
        """Create interactive Plotly heatmap."""
        fig = go.Figure(data=go.Heatmap(
            z=matrix,
            x=[f"{h:02d}:00" for h in hours],
            y=devices,
            colorscale='Viridis',
            hoverongaps=False,
            hovertemplate='Dispositivo: %{y}<br>Hora: %{x}<br>Violaciones: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Hora del Día",
            yaxis_title="Dispositivos",
            font=dict(size=12),
            width=self.config.width,
            height=self.config.height
        )
        
        return fig.to_json()
    
    def _create_matplotlib_heatmap(self, matrix: List[List[int]], 
                                  devices: List[str], hours: List[int], title: str) -> str:
        """Create matplotlib heatmap."""
        fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
        
        # Create heatmap
        im = ax.imshow(matrix, cmap='viridis', aspect='auto', interpolation='nearest')
        
        # Set ticks and labels
        ax.set_xticks(np.arange(len(hours)))
        ax.set_yticks(np.arange(len(devices)))
        ax.set_xticklabels([f"{h:02d}:00" for h in hours])
        ax.set_yticklabels(devices)
        
        # Rotate x labels for better readability
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
        
        # Add colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel('Número de Violaciones', rotation=-90, va="bottom")
        
        # Add value annotations
        for i in range(len(devices)):
            for j in range(len(hours)):
                if matrix[i][j] > 0:
                    text = ax.text(j, i, str(matrix[i][j]),
                                 ha="center", va="center", 
                                 color="white" if matrix[i][j] > np.max(matrix)/2 else "black",
                                 fontweight='bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Hora del Día', fontsize=12)
        ax.set_ylabel('Dispositivos', fontsize=12)
        
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def create_trend_analysis(self, data: Dict[str, List[Tuple[datetime, float]]],
                             title: str = "Análisis de Tendencias") -> str:
        """Create trend analysis chart with statistical annotations."""
        if self.config.interactive:
            return self._create_plotly_trend(data, title)
        else:
            return self._create_matplotlib_trend(data, title)
    
    def _create_plotly_trend(self, data: Dict[str, List[Tuple[datetime, float]]], title: str) -> str:
        """Create interactive Plotly trend chart."""
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        colors = px.colors.qualitative.Set1
        
        for i, (series_name, series_data) in enumerate(data.items()):
            timestamps, values = zip(*series_data) if series_data else ([], [])
            
            # Add main trend line
            fig.add_trace(
                go.Scatter(
                    x=timestamps,
                    y=values,
                    mode='lines+markers',
                    name=series_name,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6),
                    hovertemplate=f'{series_name}<br>Fecha: %{{x}}<br>Valor: %{{y}}<extra></extra>'
                )
            )
            
            # Add trend line if enough data points
            if len(values) > 2:
                # Calculate trend line using linear regression
                x_numeric = [(t - timestamps[0]).total_seconds() for t in timestamps]
                z = np.polyfit(x_numeric, values, 1)
                trend_values = [z[0] * x + z[1] for x in x_numeric]
                
                fig.add_trace(
                    go.Scatter(
                        x=timestamps,
                        y=trend_values,
                        mode='lines',
                        name=f'{series_name} (Tendencia)',
                        line=dict(color=colors[i % len(colors)], width=2, dash='dash'),
                        showlegend=False,
                        hoverinfo='skip'
                    )
                )
        
        fig.update_layout(
            title=title,
            xaxis_title="Fecha",
            yaxis_title="Valor",
            hovermode='x unified',
            width=self.config.width,
            height=self.config.height,
            showlegend=True
        )
        
        return fig.to_json()
    
    def _create_matplotlib_trend(self, data: Dict[str, List[Tuple[datetime, float]]], title: str) -> str:
        """Create matplotlib trend chart."""
        fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
        
        for i, (series_name, series_data) in enumerate(data.items()):
            if not series_data:
                continue
                
            timestamps, values = zip(*series_data)
            color = self.colors[i % len(self.colors)]
            
            # Plot main trend line
            ax.plot(timestamps, values, label=series_name, color=color, 
                   linewidth=2, marker='o', markersize=4)
            
            # Add trend line if enough data points
            if len(values) > 2:
                # Calculate trend line
                x_numeric = mdates.date2num(timestamps)
                z = np.polyfit(x_numeric, values, 1)
                trend_values = [z[0] * x + z[1] for x in x_numeric]
                
                ax.plot(timestamps, trend_values, color=color, 
                       linestyle='--', alpha=0.7, linewidth=1)
        
        # Format x-axis for dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
        plt.xticks(rotation=45)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Fecha', fontsize=12)
        ax.set_ylabel('Valor', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def create_performance_dashboard(self, device_metrics: List[Dict[str, Any]]) -> str:
        """Create comprehensive performance dashboard."""
        if self.config.interactive:
            return self._create_plotly_performance_dashboard(device_metrics)
        else:
            return self._create_matplotlib_performance_dashboard(device_metrics)
    
    def _create_plotly_performance_dashboard(self, device_metrics: List[Dict[str, Any]]) -> str:
        """Create interactive performance dashboard with Plotly."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Uptime por Dispositivo', 'FPS Promedio', 
                          'Violaciones Detectadas', 'Distribución de Precisión'),
            specs=[[{"type": "bar"}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "histogram"}]]
        )
        
        device_names = [d['device_id'] for d in device_metrics]
        uptime_values = [d['uptime_percentage'] for d in device_metrics]
        fps_values = [d['average_fps'] for d in device_metrics]
        violations = [d['violations_detected'] for d in device_metrics]
        accuracy_scores = [d.get('accuracy_score', 0.8) for d in device_metrics]
        
        # Uptime chart
        fig.add_trace(
            go.Bar(x=device_names, y=uptime_values, name="Uptime (%)",
                  marker_color='lightblue'),
            row=1, col=1
        )
        
        # FPS chart
        fig.add_trace(
            go.Bar(x=device_names, y=fps_values, name="FPS",
                  marker_color='lightgreen'),
            row=1, col=2
        )
        
        # Violations chart
        fig.add_trace(
            go.Bar(x=device_names, y=violations, name="Violaciones",
                  marker_color='lightcoral'),
            row=2, col=1
        )
        
        # Accuracy distribution
        fig.add_trace(
            go.Histogram(x=accuracy_scores, name="Precisión",
                        marker_color='lightyellow', nbinsx=10),
            row=2, col=2
        )
        
        fig.update_layout(
            title_text="Dashboard de Rendimiento de Dispositivos",
            showlegend=False,
            width=self.config.width,
            height=self.config.height
        )
        
        return fig.to_json()
    
    def _create_matplotlib_performance_dashboard(self, device_metrics: List[Dict[str, Any]]) -> str:
        """Create performance dashboard with matplotlib."""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(self.config.width/100, self.config.height/100))
        
        device_names = [d['device_id'] for d in device_metrics]
        uptime_values = [d['uptime_percentage'] for d in device_metrics]
        fps_values = [d['average_fps'] for d in device_metrics]
        violations = [d['violations_detected'] for d in device_metrics]
        accuracy_scores = [d.get('accuracy_score', 0.8) for d in device_metrics]
        
        # Uptime chart
        bars1 = ax1.bar(device_names, uptime_values, color=self.colors[0])
        ax1.set_title('Uptime por Dispositivo (%)')
        ax1.set_ylabel('Uptime (%)')
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar, value in zip(bars1, uptime_values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}%', ha='center', va='bottom')
        
        # FPS chart
        bars2 = ax2.bar(device_names, fps_values, color=self.colors[1])
        ax2.set_title('FPS Promedio por Dispositivo')
        ax2.set_ylabel('FPS')
        ax2.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars2, fps_values):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value:.1f}', ha='center', va='bottom')
        
        # Violations chart
        bars3 = ax3.bar(device_names, violations, color=self.colors[2])
        ax3.set_title('Violaciones Detectadas')
        ax3.set_ylabel('Número de Violaciones')
        ax3.tick_params(axis='x', rotation=45)
        
        for bar, value in zip(bars3, violations):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height,
                    f'{value}', ha='center', va='bottom')
        
        # Accuracy distribution
        ax4.hist(accuracy_scores, bins=10, color=self.colors[3], alpha=0.7, edgecolor='black')
        ax4.set_title('Distribución de Precisión')
        ax4.set_xlabel('Precisión')
        ax4.set_ylabel('Frecuencia')
        ax4.axvline(np.mean(accuracy_scores), color='red', linestyle='--', 
                   label=f'Promedio: {np.mean(accuracy_scores):.2f}')
        ax4.legend()
        
        plt.suptitle('Dashboard de Rendimiento de Dispositivos', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def create_violation_timeline(self, violations: List[Dict[str, Any]],
                                 title: str = "Línea de Tiempo de Violaciones") -> str:
        """Create violation timeline visualization."""
        if not violations:
            return self._create_empty_chart("No hay datos de violaciones disponibles")
        
        # Group violations by time intervals
        df = pd.DataFrame(violations)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['hour'] = df['timestamp'].dt.floor('H')
        
        hourly_counts = df.groupby(['hour', 'violation_type']).size().reset_index(name='count')
        
        if self.config.interactive:
            return self._create_plotly_timeline(hourly_counts, title)
        else:
            return self._create_matplotlib_timeline(hourly_counts, title)
    
    def _create_plotly_timeline(self, data: pd.DataFrame, title: str) -> str:
        """Create interactive timeline with Plotly."""
        fig = px.line(data, x='hour', y='count', color='violation_type',
                     title=title, markers=True)
        
        fig.update_layout(
            xaxis_title="Tiempo",
            yaxis_title="Número de Violaciones",
            width=self.config.width,
            height=self.config.height,
            hovermode='x unified'
        )
        
        return fig.to_json()
    
    def _create_matplotlib_timeline(self, data: pd.DataFrame, title: str) -> str:
        """Create timeline with matplotlib."""
        fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
        
        violation_types = data['violation_type'].unique()
        
        for i, vtype in enumerate(violation_types):
            type_data = data[data['violation_type'] == vtype]
            color = self.colors[i % len(self.colors)]
            
            ax.plot(type_data['hour'], type_data['count'], 
                   label=vtype, color=color, marker='o', linewidth=2)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Tiempo', fontsize=12)
        ax.set_ylabel('Número de Violaciones', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis for datetime
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def create_speed_distribution(self, speed_data: List[float],
                                 title: str = "Distribución de Velocidades") -> str:
        """Create speed distribution visualization."""
        if not speed_data:
            return self._create_empty_chart("No hay datos de velocidad disponibles")
        
        if self.config.interactive:
            return self._create_plotly_speed_distribution(speed_data, title)
        else:
            return self._create_matplotlib_speed_distribution(speed_data, title)
    
    def _create_plotly_speed_distribution(self, speed_data: List[float], title: str) -> str:
        """Create interactive speed distribution with Plotly."""
        fig = go.Figure()
        
        # Histogram
        fig.add_trace(go.Histogram(
            x=speed_data,
            nbinsx=30,
            name="Distribución",
            marker_color='lightblue',
            opacity=0.7
        ))
        
        # Add statistical lines
        mean_speed = np.mean(speed_data)
        median_speed = np.median(speed_data)
        
        fig.add_vline(x=mean_speed, line_dash="dash", line_color="red",
                     annotation_text=f"Media: {mean_speed:.1f} km/h")
        fig.add_vline(x=median_speed, line_dash="dash", line_color="green",
                     annotation_text=f"Mediana: {median_speed:.1f} km/h")
        
        fig.update_layout(
            title=title,
            xaxis_title="Velocidad (km/h)",
            yaxis_title="Frecuencia",
            width=self.config.width,
            height=self.config.height
        )
        
        return fig.to_json()
    
    def _create_matplotlib_speed_distribution(self, speed_data: List[float], title: str) -> str:
        """Create speed distribution with matplotlib."""
        fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
        
        # Create histogram
        n, bins, patches = ax.hist(speed_data, bins=30, alpha=0.7, color=self.colors[0], 
                                  edgecolor='black')
        
        # Add statistical lines
        mean_speed = np.mean(speed_data)
        median_speed = np.median(speed_data)
        
        ax.axvline(mean_speed, color='red', linestyle='--', linewidth=2,
                  label=f'Media: {mean_speed:.1f} km/h')
        ax.axvline(median_speed, color='green', linestyle='--', linewidth=2,
                  label=f'Mediana: {median_speed:.1f} km/h')
        
        # Add normal distribution overlay
        mu, sigma = np.mean(speed_data), np.std(speed_data)
        x = np.linspace(min(speed_data), max(speed_data), 100)
        y = ((1/(sigma * np.sqrt(2 * np.pi))) * 
             np.exp(-0.5 * ((x - mu) / sigma) ** 2))
        
        # Scale to match histogram
        y_scaled = y * len(speed_data) * (bins[1] - bins[0])
        ax.plot(x, y_scaled, 'k--', alpha=0.7, label='Distribución Normal')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Velocidad (km/h)', fontsize=12)
        ax.set_ylabel('Frecuencia', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def create_geographic_heatmap(self, location_data: List[Dict[str, Any]],
                                 title: str = "Mapa de Calor Geográfico") -> str:
        """Create geographic heatmap of violations."""
        # This would require actual GPS coordinates
        # For now, create a simulated geographic distribution
        
        if self.config.interactive:
            return self._create_plotly_geographic_heatmap(location_data, title)
        else:
            return self._create_matplotlib_geographic_heatmap(location_data, title)
    
    def _create_plotly_geographic_heatmap(self, location_data: List[Dict[str, Any]], title: str) -> str:
        """Create interactive geographic heatmap with Plotly."""
        # Simulate geographic data
        np.random.seed(42)
        n_points = len(location_data) if location_data else 100
        
        # Generate random coordinates (simulating city area)
        lat = np.random.normal(40.7128, 0.05, n_points)  # NYC latitude
        lon = np.random.normal(-74.0060, 0.05, n_points)  # NYC longitude
        
        fig = go.Figure(go.Densitymapbox(
            lat=lat,
            lon=lon,
            z=[1] * n_points,
            radius=10,
            showscale=True,
            colorscale="Viridis"
        ))
        
        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox=dict(center=dict(lat=40.7128, lon=-74.0060), zoom=10),
            title=title,
            width=self.config.width,
            height=self.config.height
        )
        
        return fig.to_json()
    
    def _create_matplotlib_geographic_heatmap(self, location_data: List[Dict[str, Any]], title: str) -> str:
        """Create geographic heatmap with matplotlib."""
        fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
        
        # Simulate a simple 2D heatmap representing geographic distribution
        # In a real implementation, this would use actual map data
        
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)
        
        # Create 2D histogram
        heatmap, xedges, yedges = np.histogram2d(x, y, bins=20)
        
        # Create heatmap
        im = ax.imshow(heatmap.T, origin='lower', cmap='viridis', 
                      extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]])
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Coordenada X (simulada)', fontsize=12)
        ax.set_ylabel('Coordenada Y (simulada)', fontsize=12)
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Densidad de Violaciones', rotation=270, labelpad=15)
        
        plt.tight_layout()
        
        return self._fig_to_base64(fig)
    
    def create_animated_chart(self, time_series_data: Dict[str, List[Tuple[datetime, float]]],
                             title: str = "Evolución Temporal") -> str:
        """Create animated chart showing evolution over time."""
        if not self.config.animation:
            # Create static version
            return self.create_trend_analysis(time_series_data, title)
        
        # For now, return static version (animation would require more complex setup)
        return self.create_trend_analysis(time_series_data, title + " (Animación no disponible)")
    
    def _create_empty_chart(self, message: str) -> str:
        """Create empty chart with message."""
        fig, ax = plt.subplots(figsize=(self.config.width/100, self.config.height/100))
        
        ax.text(0.5, 0.5, message, horizontalalignment='center',
               verticalalignment='center', transform=ax.transAxes,
               fontsize=16, bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
        
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert matplotlib figure to base64 string."""
        buffer = io.BytesIO()
        
        if self.config.export_format == 'svg':
            fig.savefig(buffer, format='svg', dpi=self.config.dpi, bbox_inches='tight')
            svg_data = buffer.getvalue().decode('utf-8')
            plt.close(fig)
            return f"data:image/svg+xml;utf8,{svg_data}"
        
        elif self.config.export_format == 'pdf':
            fig.savefig(buffer, format='pdf', dpi=self.config.dpi, bbox_inches='tight')
            pdf_data = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            return f"data:application/pdf;base64,{pdf_data}"
        
        else:  # PNG (default)
            fig.savefig(buffer, format='png', dpi=self.config.dpi, bbox_inches='tight')
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            plt.close(fig)
            return f"data:image/png;base64,{image_base64}"
    
    def export_chart_data(self, chart_data: Dict[str, Any], filename: str) -> str:
        """Export chart data to various formats."""
        file_path = Path(filename)
        
        if file_path.suffix.lower() == '.json':
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chart_data, f, indent=2, default=str)
        
        elif file_path.suffix.lower() == '.csv':
            # Convert to DataFrame if possible
            if isinstance(chart_data, dict) and 'data' in chart_data:
                df = pd.DataFrame(chart_data['data'])
                df.to_csv(file_path, index=False)
            else:
                # Fallback to JSON format
                with open(file_path.with_suffix('.json'), 'w', encoding='utf-8') as f:
                    json.dump(chart_data, f, indent=2, default=str)
        
        return str(file_path)


class DataExporter:
    """Utility class for exporting data in various formats."""
    
    @staticmethod
    def export_to_excel(data: Dict[str, Any], filename: str) -> str:
        """Export data to Excel file."""
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            for sheet_name, sheet_data in data.items():
                if isinstance(sheet_data, list):
                    df = pd.DataFrame(sheet_data)
                elif isinstance(sheet_data, dict):
                    df = pd.DataFrame([sheet_data])
                else:
                    df = pd.DataFrame({'data': [sheet_data]})
                
                df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        
        return filename
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str) -> str:
        """Export data to CSV file."""
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        return filename
    
    @staticmethod
    def export_to_json(data: Any, filename: str) -> str:
        """Export data to JSON file."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return filename


# Template configurations for common chart types
CHART_TEMPLATES = {
    'traffic_summary': {
        'theme': VisualizationTheme.PROFESSIONAL,
        'width': 1000,
        'height': 600,
        'interactive': True
    },
    'violation_analysis': {
        'theme': VisualizationTheme.COLORFUL,
        'width': 800,
        'height': 500,
        'interactive': True
    },
    'device_performance': {
        'theme': VisualizationTheme.MINIMAL,
        'width': 1200,
        'height': 800,
        'interactive': False
    },
    'dashboard': {
        'theme': VisualizationTheme.DARK,
        'width': 400,
        'height': 300,
        'interactive': True
    }
}