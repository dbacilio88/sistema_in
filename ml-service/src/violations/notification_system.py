"""
Notification System for Traffic Violations.

This module provides automated notification and alerting capabilities
for traffic violation detection system.
"""

import logging
import time
import json
import smtplib
import requests
from typing import List, Dict, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.image import MimeImage
from pathlib import Path
import threading
import queue
import sqlite3
from datetime import datetime
import cv2
import numpy as np

from .violation_detector import TrafficViolation, ViolationType, ViolationSeverity

logger = logging.getLogger(__name__)

class NotificationChannel(Enum):
    """Available notification channels."""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE = "file"
    API = "api"
    TELEGRAM = "telegram"
    SLACK = "slack"

class AlertPriority(Enum):
    """Alert priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class NotificationConfig:
    """Configuration for notification channels."""
    channel: NotificationChannel
    enabled: bool
    config: Dict[str, Any]
    retry_attempts: int = 3
    retry_delay: float = 5.0
    rate_limit: Optional[int] = None  # Max notifications per hour

@dataclass
class Alert:
    """Alert notification structure."""
    alert_id: str
    timestamp: float
    priority: AlertPriority
    violation: TrafficViolation
    message: str
    channels: List[NotificationChannel]
    metadata: Dict[str, Any]
    attempts: int = 0
    sent: bool = False
    error: Optional[str] = None

class NotificationSystem:
    """
    Comprehensive notification system for traffic violations.
    
    Features:
    - Multiple notification channels
    - Priority-based alerting
    - Rate limiting and retry logic
    - Template-based messages
    - Evidence attachment support
    - Real-time and batch notifications
    """
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize notification system.
        
        Args:
            config_file: Path to notification configuration file
        """
        self.notification_configs: Dict[NotificationChannel, NotificationConfig] = {}
        self.alert_queue = queue.Queue()
        self.sent_alerts: List[Alert] = []
        
        # Rate limiting tracking
        self.rate_limit_counters: Dict[NotificationChannel, List[float]] = {}
        
        # Threading for async notifications
        self.notification_thread = None
        self.running = False
        
        # Database for persistence
        self.db_path = "notifications.db"
        self._init_database()
        
        # Load configuration
        if config_file and Path(config_file).exists():
            self.load_config(config_file)
        else:
            self._setup_default_config()
        
        logger.info("NotificationSystem initialized")
    
    def _init_database(self):
        """Initialize SQLite database for notification tracking."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE,
                    timestamp REAL,
                    priority TEXT,
                    violation_id TEXT,
                    violation_type TEXT,
                    message TEXT,
                    channels TEXT,
                    sent BOOLEAN,
                    attempts INTEGER,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize notification database: {e}")
    
    def _setup_default_config(self):
        """Setup default notification configuration."""
        # Database notifications (always enabled)
        self.add_notification_config(NotificationConfig(
            channel=NotificationChannel.DATABASE,
            enabled=True,
            config={"db_path": self.db_path}
        ))
        
        # File notifications
        self.add_notification_config(NotificationConfig(
            channel=NotificationChannel.FILE,
            enabled=True,
            config={
                "log_file": "violations.log",
                "evidence_dir": "evidence"
            }
        ))
        
        # Email notifications (disabled by default)
        self.add_notification_config(NotificationConfig(
            channel=NotificationChannel.EMAIL,
            enabled=False,
            config={
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": [],
                "use_tls": True
            },
            rate_limit=50  # Max 50 emails per hour
        ))
        
        # Webhook notifications
        self.add_notification_config(NotificationConfig(
            channel=NotificationChannel.WEBHOOK,
            enabled=False,
            config={
                "url": "",
                "headers": {"Content-Type": "application/json"},
                "timeout": 10
            },
            rate_limit=100
        ))
    
    def add_notification_config(self, config: NotificationConfig):
        """Add notification channel configuration."""
        self.notification_configs[config.channel] = config
        self.rate_limit_counters[config.channel] = []
        logger.info(f"Added notification config for {config.channel.value}")
    
    def load_config(self, config_file: str):
        """Load notification configuration from file."""
        try:
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            for channel_name, channel_config in config_data.items():
                try:
                    channel = NotificationChannel(channel_name)
                    config = NotificationConfig(
                        channel=channel,
                        enabled=channel_config.get("enabled", False),
                        config=channel_config.get("config", {}),
                        retry_attempts=channel_config.get("retry_attempts", 3),
                        retry_delay=channel_config.get("retry_delay", 5.0),
                        rate_limit=channel_config.get("rate_limit")
                    )
                    self.add_notification_config(config)
                except ValueError:
                    logger.warning(f"Unknown notification channel: {channel_name}")
            
            logger.info(f"Loaded notification configuration from {config_file}")
            
        except Exception as e:
            logger.error(f"Failed to load notification config: {e}")
    
    def start(self):
        """Start notification processing thread."""
        if not self.running:
            self.running = True
            self.notification_thread = threading.Thread(target=self._process_notifications)
            self.notification_thread.daemon = True
            self.notification_thread.start()
            logger.info("Notification system started")
    
    def stop(self):
        """Stop notification processing."""
        self.running = False
        if self.notification_thread:
            self.notification_thread.join(timeout=5.0)
        logger.info("Notification system stopped")
    
    def send_violation_alert(self, violation: TrafficViolation, 
                           priority: Optional[AlertPriority] = None,
                           channels: Optional[List[NotificationChannel]] = None) -> str:
        """
        Send alert for traffic violation.
        
        Args:
            violation: Traffic violation to alert about
            priority: Alert priority (auto-determined if None)
            channels: Specific channels to use (all enabled if None)
            
        Returns:
            Alert ID
        """
        # Auto-determine priority if not specified
        if priority is None:
            priority = self._determine_priority(violation)
        
        # Determine channels if not specified
        if channels is None:
            channels = self._get_enabled_channels_for_priority(priority)
        
        # Generate alert message
        message = self._generate_alert_message(violation)
        
        # Create alert
        alert = Alert(
            alert_id=f"alert_{int(time.time())}_{violation.violation_id[:8]}",
            timestamp=time.time(),
            priority=priority,
            violation=violation,
            message=message,
            channels=channels,
            metadata={
                "violation_type": violation.violation_type.value,
                "severity": violation.severity.value,
                "location": asdict(violation.location)
            }
        )
        
        # Queue alert for processing
        self.alert_queue.put(alert)
        
        logger.info(f"Queued alert {alert.alert_id} for violation {violation.violation_id}")
        return alert.alert_id
    
    def _determine_priority(self, violation: TrafficViolation) -> AlertPriority:
        """Auto-determine alert priority based on violation."""
        if violation.severity == ViolationSeverity.CRITICAL:
            return AlertPriority.CRITICAL
        elif violation.severity == ViolationSeverity.SEVERE:
            return AlertPriority.HIGH
        elif violation.severity == ViolationSeverity.MODERATE:
            return AlertPriority.MEDIUM
        else:
            return AlertPriority.LOW
    
    def _get_enabled_channels_for_priority(self, priority: AlertPriority) -> List[NotificationChannel]:
        """Get enabled notification channels for priority level."""
        channels = []
        
        for channel, config in self.notification_configs.items():
            if not config.enabled:
                continue
            
            # Different channels for different priorities
            if priority == AlertPriority.CRITICAL:
                # All channels for critical alerts
                channels.append(channel)
            elif priority == AlertPriority.HIGH:
                # Most channels except file for high priority
                if channel != NotificationChannel.FILE:
                    channels.append(channel)
            elif priority == AlertPriority.MEDIUM:
                # Database, file, and webhook for medium priority
                if channel in [NotificationChannel.DATABASE, NotificationChannel.FILE, NotificationChannel.WEBHOOK]:
                    channels.append(channel)
            else:  # LOW priority
                # Only database and file for low priority
                if channel in [NotificationChannel.DATABASE, NotificationChannel.FILE]:
                    channels.append(channel)
        
        return channels
    
    def _generate_alert_message(self, violation: TrafficViolation) -> str:
        """Generate alert message for violation."""
        timestamp_str = datetime.fromtimestamp(violation.timestamp).strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""
🚨 TRAFFIC VIOLATION DETECTED 🚨

Violation ID: {violation.violation_id}
Time: {timestamp_str}
Type: {violation.violation_type.value.replace('_', ' ').title()}
Severity: {violation.severity.value.upper()}

Description: {violation.description}
Vehicle ID: {violation.vehicle_id}
Location: {violation.location.zone_name}

"""
        
        # Add specific details based on violation type
        if violation.violation_type == ViolationType.SPEED_VIOLATION:
            message += f"Speed Limit: {violation.speed_limit} km/h\n"
            message += f"Measured Speed: {violation.measured_speed} km/h\n"
            over_limit = violation.measured_speed - violation.speed_limit
            message += f"Over Limit: +{over_limit:.1f} km/h\n"
        
        if violation.license_plate:
            message += f"License Plate: {violation.license_plate}\n"
        
        message += f"Confidence: {violation.confidence:.2f}\n"
        message += f"Detection Confidence: {violation.detection_confidence:.2f}\n"
        
        return message.strip()
    
    def _process_notifications(self):
        """Process notification queue in background thread."""
        while self.running:
            try:
                # Get alert from queue (with timeout)
                alert = self.alert_queue.get(timeout=1.0)
                
                # Process alert
                self._send_alert(alert)
                
                # Mark task as done
                self.alert_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
    
    def _send_alert(self, alert: Alert):
        """Send alert through configured channels."""
        success_channels = []
        failed_channels = []
        
        for channel in alert.channels:
            if not self._check_rate_limit(channel):
                logger.warning(f"Rate limit exceeded for {channel.value}")
                continue
            
            try:
                success = self._send_to_channel(alert, channel)
                if success:
                    success_channels.append(channel)
                    self._update_rate_limit(channel)
                else:
                    failed_channels.append(channel)
            except Exception as e:
                logger.error(f"Failed to send alert via {channel.value}: {e}")
                failed_channels.append(channel)
                alert.error = str(e)
        
        # Update alert status
        alert.attempts += 1
        alert.sent = len(success_channels) > 0
        
        # Store alert
        self.sent_alerts.append(alert)
        self._store_alert_in_db(alert)
        
        if success_channels:
            logger.info(f"Alert {alert.alert_id} sent via: {[c.value for c in success_channels]}")
        
        if failed_channels:
            logger.warning(f"Alert {alert.alert_id} failed via: {[c.value for c in failed_channels]}")
            
            # Retry logic for failed channels
            if alert.attempts < 3:  # Max 3 attempts
                # Re-queue with only failed channels after delay
                time.sleep(5.0)
                retry_alert = Alert(
                    alert_id=alert.alert_id + f"_retry_{alert.attempts}",
                    timestamp=time.time(),
                    priority=alert.priority,
                    violation=alert.violation,
                    message=alert.message,
                    channels=failed_channels,
                    metadata=alert.metadata,
                    attempts=alert.attempts
                )
                self.alert_queue.put(retry_alert)
    
    def _send_to_channel(self, alert: Alert, channel: NotificationChannel) -> bool:
        """Send alert to specific channel."""
        config = self.notification_configs.get(channel)
        if not config or not config.enabled:
            return False
        
        try:
            if channel == NotificationChannel.DATABASE:
                return self._send_database_notification(alert, config)
            elif channel == NotificationChannel.FILE:
                return self._send_file_notification(alert, config)
            elif channel == NotificationChannel.EMAIL:
                return self._send_email_notification(alert, config)
            elif channel == NotificationChannel.WEBHOOK:
                return self._send_webhook_notification(alert, config)
            elif channel == NotificationChannel.API:
                return self._send_api_notification(alert, config)
            else:
                logger.warning(f"Unsupported notification channel: {channel.value}")
                return False
        except Exception as e:
            logger.error(f"Error sending to {channel.value}: {e}")
            return False
    
    def _send_database_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send notification to database."""
        try:
            conn = sqlite3.connect(config.config["db_path"])
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO notifications 
                (alert_id, timestamp, priority, violation_id, violation_type, 
                 message, channels, sent, attempts, error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.alert_id,
                alert.timestamp,
                alert.priority.value,
                alert.violation.violation_id,
                alert.violation.violation_type.value,
                alert.message,
                json.dumps([c.value for c in alert.channels]),
                alert.sent,
                alert.attempts,
                alert.error
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Database notification failed: {e}")
            return False
    
    def _send_file_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send notification to log file."""
        try:
            log_file = config.config.get("log_file", "violations.log")
            
            with open(log_file, 'a') as f:
                timestamp_str = datetime.fromtimestamp(alert.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"[{timestamp_str}] {alert.priority.value.upper()} - {alert.alert_id}\n"
                log_entry += f"{alert.message}\n"
                log_entry += "-" * 80 + "\n"
                f.write(log_entry)
            
            # Save evidence if available
            evidence_dir = Path(config.config.get("evidence_dir", "evidence"))
            if alert.violation.evidence_frame is not None:
                evidence_dir.mkdir(exist_ok=True)
                evidence_file = evidence_dir / f"{alert.alert_id}_evidence.jpg"
                cv2.imwrite(str(evidence_file), alert.violation.evidence_frame)
            
            return True
            
        except Exception as e:
            logger.error(f"File notification failed: {e}")
            return False
    
    def _send_email_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send email notification."""
        try:
            email_config = config.config
            
            msg = MimeMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = ', '.join(email_config['to_emails'])
            msg['Subject'] = f"Traffic Violation Alert - {alert.violation.violation_type.value.title()}"
            
            # Add text content
            msg.attach(MimeText(alert.message, 'plain'))
            
            # Add evidence image if available
            if alert.violation.evidence_frame is not None:
                # Convert frame to JPEG
                _, img_buffer = cv2.imencode('.jpg', alert.violation.evidence_frame)
                img_data = img_buffer.tobytes()
                
                img_attachment = MimeImage(img_data)
                img_attachment.add_header('Content-Disposition', 
                                        f'attachment; filename={alert.alert_id}_evidence.jpg')
                msg.attach(img_attachment)
            
            # Send email
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            if email_config.get('use_tls', True):
                server.starttls()
            server.login(email_config['username'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            return True
            
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            return False
    
    def _send_webhook_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send webhook notification."""
        try:
            webhook_config = config.config
            
            payload = {
                "alert_id": alert.alert_id,
                "timestamp": alert.timestamp,
                "priority": alert.priority.value,
                "violation": {
                    "id": alert.violation.violation_id,
                    "type": alert.violation.violation_type.value,
                    "severity": alert.violation.severity.value,
                    "description": alert.violation.description,
                    "vehicle_id": alert.violation.vehicle_id,
                    "location": asdict(alert.violation.location),
                    "speed_limit": alert.violation.speed_limit,
                    "measured_speed": alert.violation.measured_speed,
                    "license_plate": alert.violation.license_plate,
                    "confidence": alert.violation.confidence
                },
                "message": alert.message
            }
            
            response = requests.post(
                webhook_config['url'],
                json=payload,
                headers=webhook_config.get('headers', {}),
                timeout=webhook_config.get('timeout', 10)
            )
            
            return response.status_code == 200
            
        except Exception as e:
            logger.error(f"Webhook notification failed: {e}")
            return False
    
    def _send_api_notification(self, alert: Alert, config: NotificationConfig) -> bool:
        """Send API notification."""
        # Similar to webhook but with different endpoint/format
        return self._send_webhook_notification(alert, config)
    
    def _check_rate_limit(self, channel: NotificationChannel) -> bool:
        """Check if channel is within rate limits."""
        config = self.notification_configs.get(channel)
        if not config or not config.rate_limit:
            return True
        
        current_time = time.time()
        hour_ago = current_time - 3600  # 1 hour ago
        
        # Clean old timestamps
        self.rate_limit_counters[channel] = [
            timestamp for timestamp in self.rate_limit_counters[channel]
            if timestamp > hour_ago
        ]
        
        # Check if under limit
        return len(self.rate_limit_counters[channel]) < config.rate_limit
    
    def _update_rate_limit(self, channel: NotificationChannel):
        """Update rate limit counter for channel."""
        self.rate_limit_counters[channel].append(time.time())
    
    def _store_alert_in_db(self, alert: Alert):
        """Store alert in database for tracking."""
        try:
            self._send_database_notification(alert, self.notification_configs[NotificationChannel.DATABASE])
        except Exception as e:
            logger.error(f"Failed to store alert in database: {e}")
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get notification system statistics."""
        total_alerts = len(self.sent_alerts)
        sent_count = len([a for a in self.sent_alerts if a.sent])
        
        channel_stats = {}
        for channel in NotificationChannel:
            channel_alerts = [a for a in self.sent_alerts if channel in a.channels]
            channel_stats[channel.value] = {
                "total": len(channel_alerts),
                "sent": len([a for a in channel_alerts if a.sent]),
                "rate_limit_count": len(self.rate_limit_counters.get(channel, []))
            }
        
        return {
            "total_alerts": total_alerts,
            "sent_alerts": sent_count,
            "failed_alerts": total_alerts - sent_count,
            "success_rate": sent_count / max(1, total_alerts),
            "queue_size": self.alert_queue.qsize(),
            "channel_statistics": channel_stats
        }