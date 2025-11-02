"""
Django API Service - Handles communication with Django backend
"""
import httpx
from typing import Dict, Any, Optional
from datetime import datetime
import uuid

from app.core import get_logger, settings

logger = get_logger(__name__)


class DjangoAPIService:
    """Service for interacting with Django REST API"""
    
    def __init__(self):
        self.base_url = settings.DJANGO_API_URL
        self.timeout = settings.DJANGO_API_TIMEOUT
        
    async def create_infraction(
        self,
        infraction_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new infraction in Django backend
        
        Args:
            infraction_data: Infraction details
            
        Returns:
            Created infraction data or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/infractions/",
                    json=infraction_data
                )
                
                if response.status_code in [200, 201]:
                    logger.info(
                        "Infraction created successfully",
                        infraction_id=response.json().get('id')
                    )
                    return response.json()
                else:
                    logger.error(
                        "Failed to create infraction",
                        status_code=response.status_code,
                        response=response.text
                    )
                    return None
                    
        except Exception as e:
            logger.error(f"Error creating infraction: {str(e)}")
            return None
    
    async def get_or_create_vehicle(
        self,
        license_plate: str,
        vehicle_type: str = 'car'
    ) -> Optional[Dict[str, Any]]:
        """
        Get existing vehicle or create new one
        
        Args:
            license_plate: Vehicle license plate
            vehicle_type: Type of vehicle
            
        Returns:
            Vehicle data or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Try to get existing vehicle
                response = await client.get(
                    f"{self.base_url}/api/vehicles/",
                    params={'license_plate': license_plate}
                )
                
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    if results:
                        logger.info(f"Vehicle found: {license_plate}")
                        return results[0]
                
                # Create new vehicle if not found
                vehicle_data = {
                    'license_plate': license_plate,
                    'vehicle_type': vehicle_type,
                }
                
                response = await client.post(
                    f"{self.base_url}/api/vehicles/",
                    json=vehicle_data
                )
                
                if response.status_code in [200, 201]:
                    logger.info(f"Vehicle created: {license_plate}")
                    return response.json()
                else:
                    logger.error(
                        "Failed to create vehicle",
                        license_plate=license_plate,
                        status_code=response.status_code
                    )
                    return None
                    
        except Exception as e:
            logger.error(f"Error with vehicle: {str(e)}")
            return None
    
    async def get_device(self, device_code: str) -> Optional[Dict[str, Any]]:
        """Get device information by code"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/devices/",
                    params={'code': device_code}
                )
                
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    if results:
                        return results[0]
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting device: {str(e)}")
            return None
    
    async def get_zone(self, zone_code: str) -> Optional[Dict[str, Any]]:
        """Get zone information by code"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/api/zones/",
                    params={'code': zone_code}
                )
                
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    if results:
                        return results[0]
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting zone: {str(e)}")
            return None
    
    async def upload_evidence_to_minio(
        self,
        image_data: bytes,
        infraction_id: str,
        file_type: str = 'snapshot'
    ) -> Optional[str]:
        """
        Upload evidence image to MinIO via Django API
        
        Args:
            image_data: Image bytes
            infraction_id: Infraction UUID
            file_type: 'snapshot' or 'video'
            
        Returns:
            URL of uploaded file or None
        """
        try:
            # In a real implementation, this would upload directly to MinIO
            # For MVP, we can store the URL reference
            # TODO: Implement MinIO upload
            logger.info(f"Evidence upload requested for infraction {infraction_id}")
            return f"s3://traffic-evidence/{infraction_id}/{file_type}.jpg"
            
        except Exception as e:
            logger.error(f"Error uploading evidence: {str(e)}")
            return None


# Global Django API service instance
django_api = DjangoAPIService()
