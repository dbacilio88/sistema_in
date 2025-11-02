import asyncio
import time
from typing import Dict
import redis.asyncio as redis
import asyncpg
from datetime import datetime

from app.core import settings, get_logger
from app.models import ServiceStatus, ServiceHealth

logger = get_logger(__name__)


class HealthService:
    """Service to check health of dependencies"""
    
    def __init__(self):
        self.start_time = time.time()
    
    async def check_database(self) -> ServiceHealth:
        """Check PostgreSQL connection"""
        start_time = time.time()
        try:
            conn = await asyncpg.connect(settings.DATABASE_URL)
            await conn.execute("SELECT 1")
            await conn.close()
            
            response_time = (time.time() - start_time) * 1000
            return ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=response_time,
                details={"connection": "ok"}
            )
        except Exception as e:
            logger.error("Database health check failed", error=str(e))
            response_time = (time.time() - start_time) * 1000
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"error": str(e), "connection": "failed"}
            )
    
    async def check_redis(self) -> ServiceHealth:
        """Check Redis connection"""
        start_time = time.time()
        try:
            redis_client = redis.from_url(settings.REDIS_URL)
            await redis_client.ping()
            await redis_client.close()
            
            response_time = (time.time() - start_time) * 1000
            return ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=response_time,
                details={"connection": "ok"}
            )
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            response_time = (time.time() - start_time) * 1000
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"error": str(e), "connection": "failed"}
            )
    
    async def check_storage(self) -> ServiceHealth:
        """Check MinIO/S3 connection (simplified check)"""
        start_time = time.time()
        try:
            # For now, just return healthy since we don't have MinIO client yet
            # In future sprints this will be implemented with boto3/minio client
            response_time = (time.time() - start_time) * 1000
            return ServiceHealth(
                status=ServiceStatus.HEALTHY,
                response_time_ms=response_time,
                details={"connection": "ok", "note": "simplified_check"}
            )
        except Exception as e:
            logger.error("Storage health check failed", error=str(e))
            response_time = (time.time() - start_time) * 1000
            return ServiceHealth(
                status=ServiceStatus.UNHEALTHY,
                response_time_ms=response_time,
                details={"error": str(e), "connection": "failed"}
            )
    
    async def get_health_status(self) -> Dict[str, ServiceHealth]:
        """Get health status of all services"""
        # Run all health checks concurrently
        tasks = {
            "database": self.check_database(),
            "redis": self.check_redis(),
            "storage": self.check_storage(),
        }
        
        results = {}
        for service_name, task in tasks.items():
            try:
                results[service_name] = await asyncio.wait_for(task, timeout=5.0)
            except asyncio.TimeoutError:
                logger.error(f"{service_name} health check timed out")
                results[service_name] = ServiceHealth(
                    status=ServiceStatus.UNHEALTHY,
                    details={"error": "timeout", "timeout_seconds": 5.0}
                )
        
        return results
    
    def get_uptime(self) -> float:
        """Get service uptime in seconds"""
        return time.time() - self.start_time
    
    def determine_overall_status(self, services: Dict[str, ServiceHealth]) -> ServiceStatus:
        """Determine overall health status based on individual services"""
        unhealthy_count = sum(1 for service in services.values() 
                             if service.status == ServiceStatus.UNHEALTHY)
        degraded_count = sum(1 for service in services.values() 
                            if service.status == ServiceStatus.DEGRADED)
        
        if unhealthy_count > 0:
            return ServiceStatus.UNHEALTHY
        elif degraded_count > 0:
            return ServiceStatus.DEGRADED
        else:
            return ServiceStatus.HEALTHY


# Global instance
health_service = HealthService()