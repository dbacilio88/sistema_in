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
        logger.info(f"🔗 DjangoAPIService initialized with URL: {self.base_url}")
        logger.info(f"⏱️  Timeout: {self.timeout}s")
        
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
            logger.info(f"📤 Attempting to create infraction: type={infraction_data.get('infraction_type')}, plate={infraction_data.get('license_plate_detected', 'N/A')}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/api/infractions/"
                logger.debug(f"POST {url}")
                
                response = await client.post(
                    url,
                    json=infraction_data
                )
                
                logger.info(f"📥 Django API response: status={response.status_code}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(
                        f"✅ Infraction created successfully: "
                        f"code={result.get('infraction_code')}, "
                        f"id={result.get('id')}, "
                        f"type={result.get('infraction_type')}"
                    )
                    return result
                else:
                    logger.error(
                        f"❌ Failed to create infraction: "
                        f"status={response.status_code}, "
                        f"response={response.text[:200]}"
                    )
                    return None
                    
        except httpx.ConnectError as e:
            logger.error(f"🔌 Connection error to Django API ({self.base_url}): {str(e)}")
            logger.error("⚠️ Verifica que el backend Django esté corriendo en el puerto correcto")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"⏱️ Timeout connecting to Django API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Error creating infraction: {str(e)}", exc_info=True)
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
    
    async def predict_recidivism(
        self,
        driver_dni: str,
        infraction_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Request ML recidivism prediction for a driver
        
        Args:
            driver_dni: Driver's DNI/document number
            infraction_id: UUID of the infraction
            
        Returns:
            Prediction result or None
        """
        try:
            logger.info(f"🤖 Requesting ML prediction for driver {driver_dni}, infraction {infraction_id}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = f"{self.base_url}/api/ml/predictions/recidivism/"
                
                payload = {
                    "driver_dni": driver_dni,
                    "infraction_id": infraction_id
                }
                
                logger.debug(f"POST {url} with payload: {payload}")
                
                response = await client.post(
                    url,
                    json=payload
                )
                
                logger.info(f"📥 ML API response: status={response.status_code}")
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    logger.info(
                        f"✅ ML prediction successful: "
                        f"risk={result.get('recidivism_probability', 0)*100:.1f}%, "
                        f"category={result.get('risk_category')}, "
                        f"time={result.get('prediction_time_ms', 0):.2f}ms"
                    )
                    return result
                else:
                    logger.error(
                        f"❌ ML prediction failed: "
                        f"status={response.status_code}, "
                        f"response={response.text[:200]}"
                    )
                    return None
                    
        except httpx.ConnectError as e:
            logger.error(f"🔌 Connection error to ML API: {str(e)}")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"⏱️ Timeout calling ML API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"❌ Error requesting ML prediction: {str(e)}", exc_info=True)
            return None


# Global Django API service instance
django_api = DjangoAPIService()
