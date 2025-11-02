"""
Real-time monitoring and metrics system for traffic analysis.

Provides comprehensive monitoring, alerting, and performance metrics
for the real-time traffic analysis pipeline.
"""

import time
import threading
import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from collections import defaultdict, deque
import json
import psutil
import statistics
from datetime import datetime, timedelta

from .analysis_pipeline import StreamMetrics, ProcessingResult
from ..violations.violation_detector import ViolationType, ViolationSeverity


@dataclass
class SystemMetrics:
    """System-wide performance metrics."""
    
    # CPU and Memory
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    memory_used_mb: float = 0.0
    memory_available_mb: float = 0.0
    
    # Disk usage
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_free_gb: float = 0.0
    
    # Network (if applicable)
    network_bytes_sent: int = 0
    network_bytes_recv: int = 0
    
    # Process specific
    process_cpu_percent: float = 0.0
    process_memory_mb: float = 0.0
    process_threads: int = 0
    
    # GPU (if available)
    gpu_percent: Optional[float] = None
    gpu_memory_percent: Optional[float] = None
    gpu_memory_used_mb: Optional[float] = None
    
    # Temperature (if available)
    cpu_temperature: Optional[float] = None
    gpu_temperature: Optional[float] = None


@dataclass
class AlertRule:
    """Configuration for monitoring alerts."""
    
    rule_id: str
    name: str
    description: str
    metric_path: str  # e.g., "fps", "cpu_percent", "violations_per_minute"
    threshold: float
    comparison: str  # "greater", "less", "equal"
    duration_seconds: float  # How long condition must persist
    enabled: bool = True
    
    # Alert behavior
    cooldown_seconds: float = 300.0  # 5 minutes default
    severity: str = "warning"  # "info", "warning", "error", "critical"
    
    # Notification settings
    notify_channels: List[str] = field(default_factory=list)
    
    # Internal state
    last_triggered: Optional[float] = None
    condition_start: Optional[float] = None


@dataclass
class Alert:
    """Generated alert from monitoring rules."""
    
    alert_id: str
    rule_id: str
    timestamp: float
    severity: str
    title: str
    description: str
    metric_value: float
    threshold: float
    device_id: Optional[str] = None
    resolved: bool = False
    resolved_at: Optional[float] = None


class PerformanceMonitor:
    """
    Performance monitoring for real-time traffic analysis system.
    
    Monitors system resources, pipeline performance, and generates alerts
    based on configurable rules.
    """
    
    def __init__(self, monitoring_interval: float = 5.0):
        """
        Initialize performance monitor.
        
        Args:
            monitoring_interval: Seconds between monitoring cycles
        """
        self.monitoring_interval = monitoring_interval
        self.logger = logging.getLogger("performance_monitor")
        
        # System monitoring
        self.system_metrics = SystemMetrics()
        self.system_metrics_history = deque(maxlen=720)  # 1 hour at 5s intervals
        
        # Pipeline monitoring
        self.pipeline_metrics: Dict[str, StreamMetrics] = {}
        self.pipeline_metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=720))
        
        # Aggregated metrics
        self.aggregated_metrics = {}
        self.aggregated_history = deque(maxlen=720)
        
        # Alert system
        self.alert_rules: Dict[str, AlertRule] = {}
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history = deque(maxlen=1000)
        
        # Callbacks
        self.alert_callbacks: List[Callable[[Alert], None]] = []
        self.metrics_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        # Monitoring thread
        self.monitoring_thread: Optional[threading.Thread] = None
        self.is_monitoring = False
        self._lock = threading.Lock()
        
        # Initialize system monitoring
        self.process = psutil.Process()
        self._setup_default_alerts()
    
    def _setup_default_alerts(self):
        """Setup default monitoring alert rules."""
        default_rules = [
            AlertRule(
                rule_id="high_cpu",
                name="High CPU Usage",
                description="CPU usage exceeds 80%",
                metric_path="system.cpu_percent",
                threshold=80.0,
                comparison="greater",
                duration_seconds=30.0,
                severity="warning"
            ),
            AlertRule(
                rule_id="high_memory",
                name="High Memory Usage", 
                description="Memory usage exceeds 85%",
                metric_path="system.memory_percent",
                threshold=85.0,
                comparison="greater",
                duration_seconds=60.0,
                severity="warning"
            ),
            AlertRule(
                rule_id="low_fps",
                name="Low FPS",
                description="Processing FPS below 10",
                metric_path="aggregated.avg_fps",
                threshold=10.0,
                comparison="less",
                duration_seconds=30.0,
                severity="error"
            ),
            AlertRule(
                rule_id="high_latency",
                name="High Processing Latency",
                description="Average latency exceeds 500ms",
                metric_path="aggregated.avg_latency_ms",
                threshold=500.0,
                comparison="greater",
                duration_seconds=60.0,
                severity="warning"
            ),
            AlertRule(
                rule_id="frequent_errors",
                name="Frequent Processing Errors",
                description="Error rate exceeds 5%",
                metric_path="aggregated.error_rate",
                threshold=0.05,
                comparison="greater",
                duration_seconds=120.0,
                severity="error"
            ),
            AlertRule(
                rule_id="disk_space_low",
                name="Low Disk Space",
                description="Disk usage exceeds 90%",
                metric_path="system.disk_percent",
                threshold=90.0,
                comparison="greater",
                duration_seconds=300.0,
                severity="critical"
            )
        ]
        
        for rule in default_rules:
            self.alert_rules[rule.rule_id] = rule
    
    def start_monitoring(self):
        """Start the monitoring system."""
        if self.is_monitoring:
            self.logger.warning("Monitoring already running")
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        self.logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.is_monitoring = False
        
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10.0)
        
        self.logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                start_time = time.time()
                
                # Collect system metrics
                self._collect_system_metrics()
                
                # Update aggregated metrics
                self._update_aggregated_metrics()
                
                # Check alert rules
                self._check_alert_rules()
                
                # Store metrics history
                with self._lock:
                    self.system_metrics_history.append({
                        'timestamp': time.time(),
                        'metrics': self.system_metrics.__dict__.copy()
                    })
                    
                    self.aggregated_history.append({
                        'timestamp': time.time(),
                        'metrics': self.aggregated_metrics.copy()
                    })
                
                # Call metrics callbacks
                for callback in self.metrics_callbacks:
                    try:
                        callback(self._get_all_metrics())
                    except Exception as e:
                        self.logger.error(f"Metrics callback error: {e}")
                
                # Sleep for remaining interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.monitoring_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.monitoring_interval)
    
    def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            # CPU and Memory
            self.system_metrics.cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            self.system_metrics.memory_percent = memory.percent
            self.system_metrics.memory_used_mb = memory.used / 1024 / 1024
            self.system_metrics.memory_available_mb = memory.available / 1024 / 1024
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.system_metrics.disk_percent = disk.percent
            self.system_metrics.disk_used_gb = disk.used / 1024 / 1024 / 1024
            self.system_metrics.disk_free_gb = disk.free / 1024 / 1024 / 1024
            
            # Network
            net_io = psutil.net_io_counters()
            self.system_metrics.network_bytes_sent = net_io.bytes_sent
            self.system_metrics.network_bytes_recv = net_io.bytes_recv
            
            # Process specific
            self.system_metrics.process_cpu_percent = self.process.cpu_percent()
            process_memory = self.process.memory_info()
            self.system_metrics.process_memory_mb = process_memory.rss / 1024 / 1024
            self.system_metrics.process_threads = self.process.num_threads()
            
            # GPU metrics (if available)
            try:
                import GPUtil
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]  # Use first GPU
                    self.system_metrics.gpu_percent = gpu.load * 100
                    self.system_metrics.gpu_memory_percent = gpu.memoryUtil * 100
                    self.system_metrics.gpu_memory_used_mb = gpu.memoryUsed
            except (ImportError, Exception):
                # GPU monitoring not available
                pass
            
            # Temperature monitoring (if available)
            try:
                temps = psutil.sensors_temperatures()
                if 'coretemp' in temps:
                    cpu_temps = [t.current for t in temps['coretemp']]
                    self.system_metrics.cpu_temperature = max(cpu_temps)
            except (AttributeError, Exception):
                # Temperature monitoring not available
                pass
                
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _update_aggregated_metrics(self):
        """Update aggregated metrics across all pipelines."""
        if not self.pipeline_metrics:
            self.aggregated_metrics = {}
            return
        
        # Aggregate pipeline metrics
        total_frames = sum(m.frames_processed for m in self.pipeline_metrics.values())
        total_detections = sum(m.detections_count for m in self.pipeline_metrics.values())
        total_violations = sum(m.violations_count for m in self.pipeline_metrics.values())
        total_errors = sum(m.errors_count for m in self.pipeline_metrics.values())
        
        active_pipelines = len([m for m in self.pipeline_metrics.values() if m.fps > 0])
        avg_fps = statistics.mean([m.fps for m in self.pipeline_metrics.values() if m.fps > 0]) if active_pipelines > 0 else 0
        avg_latency = statistics.mean([m.avg_latency_ms for m in self.pipeline_metrics.values() if m.avg_latency_ms > 0]) if active_pipelines > 0 else 0
        
        error_rate = total_errors / total_frames if total_frames > 0 else 0
        detection_rate = total_detections / total_frames if total_frames > 0 else 0
        violation_rate = total_violations / total_frames if total_frames > 0 else 0
        
        self.aggregated_metrics = {
            'total_pipelines': len(self.pipeline_metrics),
            'active_pipelines': active_pipelines,
            'total_frames': total_frames,
            'total_detections': total_detections,
            'total_violations': total_violations,
            'total_errors': total_errors,
            'avg_fps': avg_fps,
            'avg_latency_ms': avg_latency,
            'error_rate': error_rate,
            'detection_rate': detection_rate,
            'violation_rate': violation_rate
        }
    
    def _check_alert_rules(self):
        """Check all alert rules and generate alerts."""
        current_time = time.time()
        all_metrics = self._get_all_metrics()
        
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            try:
                # Get metric value
                metric_value = self._get_metric_value(all_metrics, rule.metric_path)
                if metric_value is None:
                    continue
                
                # Check condition
                condition_met = False
                if rule.comparison == "greater":
                    condition_met = metric_value > rule.threshold
                elif rule.comparison == "less":
                    condition_met = metric_value < rule.threshold
                elif rule.comparison == "equal":
                    condition_met = abs(metric_value - rule.threshold) < 0.01
                
                if condition_met:
                    # Condition is met
                    if rule.condition_start is None:
                        rule.condition_start = current_time
                    
                    # Check if condition has persisted long enough
                    if (current_time - rule.condition_start) >= rule.duration_seconds:
                        # Check cooldown
                        if (rule.last_triggered is None or 
                            (current_time - rule.last_triggered) >= rule.cooldown_seconds):
                            
                            self._trigger_alert(rule, metric_value, current_time)
                            rule.last_triggered = current_time
                else:
                    # Condition not met, reset
                    rule.condition_start = None
                
            except Exception as e:
                self.logger.error(f"Error checking alert rule {rule.rule_id}: {e}")
    
    def _get_metric_value(self, metrics: Dict[str, Any], path: str) -> Optional[float]:
        """Get metric value from nested dictionary using dot notation."""
        try:
            parts = path.split('.')
            value = metrics
            
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return None
            
            return float(value) if value is not None else None
            
        except (ValueError, TypeError):
            return None
    
    def _trigger_alert(self, rule: AlertRule, metric_value: float, timestamp: float):
        """Trigger an alert."""
        alert_id = f"{rule.rule_id}_{int(timestamp)}"
        
        alert = Alert(
            alert_id=alert_id,
            rule_id=rule.rule_id,
            timestamp=timestamp,
            severity=rule.severity,
            title=rule.name,
            description=f"{rule.description}. Current value: {metric_value:.2f}, Threshold: {rule.threshold:.2f}",
            metric_value=metric_value,
            threshold=rule.threshold
        )
        
        # Store alert
        with self._lock:
            self.active_alerts[alert_id] = alert
            self.alert_history.append(alert)
        
        self.logger.warning(f"Alert triggered: {alert.title} - {alert.description}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback error: {e}")
    
    def update_pipeline_metrics(self, device_id: str, metrics: StreamMetrics):
        """Update metrics for a specific pipeline."""
        with self._lock:
            self.pipeline_metrics[device_id] = metrics
            
            # Store in history
            self.pipeline_metrics_history[device_id].append({
                'timestamp': time.time(),
                'metrics': {
                    'frames_processed': metrics.frames_processed,
                    'fps': metrics.fps,
                    'avg_latency_ms': metrics.avg_latency_ms,
                    'detections_count': metrics.detections_count,
                    'violations_count': metrics.violations_count,
                    'errors_count': metrics.errors_count
                }
            })
    
    def add_alert_rule(self, rule: AlertRule):
        """Add a new alert rule."""
        self.alert_rules[rule.rule_id] = rule
        self.logger.info(f"Added alert rule: {rule.name}")
    
    def remove_alert_rule(self, rule_id: str):
        """Remove an alert rule."""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            self.logger.info(f"Removed alert rule: {rule_id}")
    
    def resolve_alert(self, alert_id: str):
        """Resolve an active alert."""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolved = True
            alert.resolved_at = time.time()
            del self.active_alerts[alert_id]
            
            self.logger.info(f"Alert resolved: {alert.title}")
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        with self._lock:
            return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """Get alert history for specified hours."""
        cutoff_time = time.time() - (hours * 3600)
        
        with self._lock:
            return [alert for alert in self.alert_history if alert.timestamp >= cutoff_time]
    
    def _get_all_metrics(self) -> Dict[str, Any]:
        """Get all metrics in a single dictionary."""
        return {
            'system': self.system_metrics.__dict__,
            'aggregated': self.aggregated_metrics,
            'pipelines': {
                device_id: {
                    'frames_processed': metrics.frames_processed,
                    'fps': metrics.fps,
                    'avg_latency_ms': metrics.avg_latency_ms,
                    'detections_count': metrics.detections_count,
                    'violations_count': metrics.violations_count,
                    'errors_count': metrics.errors_count
                }
                for device_id, metrics in self.pipeline_metrics.items()
            }
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            'monitoring': {
                'is_active': self.is_monitoring,
                'interval_seconds': self.monitoring_interval,
                'uptime_seconds': time.time() - self.start_time if hasattr(self, 'start_time') else 0
            },
            'alerts': {
                'active_count': len(self.active_alerts),
                'total_rules': len(self.alert_rules),
                'recent_alerts': len(self.get_alert_history(1))  # Last hour
            },
            'metrics': self._get_all_metrics()
        }
    
    def add_alert_callback(self, callback: Callable[[Alert], None]):
        """Add callback for alert notifications."""
        self.alert_callbacks.append(callback)
    
    def add_metrics_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """Add callback for metrics updates."""
        self.metrics_callbacks.append(callback)


class ViolationAnalytics:
    """
    Analytics system for tracking violation patterns and trends.
    """
    
    def __init__(self, retention_days: int = 30):
        """
        Initialize violation analytics.
        
        Args:
            retention_days: Days to retain analytics data
        """
        self.retention_days = retention_days
        self.logger = logging.getLogger("violation_analytics")
        
        # Violation tracking
        self.violation_history = deque(maxlen=10000)  # Keep last 10k violations
        self.violation_stats = defaultdict(int)
        self.hourly_stats = defaultdict(lambda: defaultdict(int))
        self.daily_stats = defaultdict(lambda: defaultdict(int))
        
        # Location-based analytics
        self.location_stats = defaultdict(lambda: defaultdict(int))
        self.hotspot_analysis = {}
        
        # Temporal analysis
        self.time_patterns = defaultdict(list)
        self.trend_analysis = {}
        
        # Real-time metrics
        self.current_hour_violations = defaultdict(int)
        self.violations_per_minute = deque(maxlen=60)  # Last 60 minutes
        
        self._lock = threading.Lock()
    
    def record_violation(self, violation_type: str, device_id: str, timestamp: float = None):
        """Record a new violation for analytics."""
        if timestamp is None:
            timestamp = time.time()
        
        dt = datetime.fromtimestamp(timestamp)
        hour_key = dt.strftime("%Y-%m-%d %H")
        day_key = dt.strftime("%Y-%m-%d")
        
        with self._lock:
            # Basic tracking
            self.violation_history.append({
                'type': violation_type,
                'device_id': device_id,
                'timestamp': timestamp
            })
            
            # Statistics
            self.violation_stats[violation_type] += 1
            self.hourly_stats[hour_key][violation_type] += 1
            self.daily_stats[day_key][violation_type] += 1
            self.location_stats[device_id][violation_type] += 1
            
            # Current hour tracking
            current_hour = datetime.now().strftime("%Y-%m-%d %H")
            if hour_key == current_hour:
                self.current_hour_violations[violation_type] += 1
    
    def get_violation_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get violation trends for specified period."""
        cutoff_time = time.time() - (hours * 3600)
        
        with self._lock:
            recent_violations = [
                v for v in self.violation_history 
                if v['timestamp'] >= cutoff_time
            ]
        
        # Count by type
        type_counts = defaultdict(int)
        hourly_counts = defaultdict(lambda: defaultdict(int))
        
        for violation in recent_violations:
            type_counts[violation['type']] += 1
            
            hour = datetime.fromtimestamp(violation['timestamp']).strftime("%H")
            hourly_counts[hour][violation['type']] += 1
        
        return {
            'period_hours': hours,
            'total_violations': len(recent_violations),
            'by_type': dict(type_counts),
            'by_hour': dict(hourly_counts),
            'violations_per_hour': len(recent_violations) / hours if hours > 0 else 0
        }
    
    def get_hotspot_analysis(self) -> Dict[str, Any]:
        """Analyze violation hotspots by location."""
        with self._lock:
            location_totals = {
                device_id: sum(type_counts.values())
                for device_id, type_counts in self.location_stats.items()
            }
        
        # Sort by total violations
        sorted_locations = sorted(
            location_totals.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        return {
            'hotspots': sorted_locations[:10],  # Top 10
            'total_locations': len(location_totals),
            'location_details': dict(self.location_stats)
        }
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current violation statistics."""
        with self._lock:
            return {
                'current_hour': dict(self.current_hour_violations),
                'total_violations': len(self.violation_history),
                'total_by_type': dict(self.violation_stats),
                'active_locations': len(self.location_stats)
            }