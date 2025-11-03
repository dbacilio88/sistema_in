""""""

Service layer for infractions managementService layer for infraction management

""""""

import loggingimport logging

from typing import List, Dict, Any, Optionalfrom datetime import datetime

from django.utils import timezonefrom decimal import Decimal

from django.db import transactionfrom typing import Dict, Optional, List

from datetime import datetimefrom django.utils import timezone

from django.db import transaction

from .models import Infraction, InfractionEventfrom .models import Infraction

from devices.models import Device, Zonefrom devices.models import Device, Zone

from vehicles.models import Vehiclefrom vehicles.models import Vehicle



logger = logging.getLogger(__name__)logger = logging.getLogger(__name__)





class InfractionService:class InfractionService:

    """Service for managing infractions and their lifecycle"""    """Service for creating and managing infractions from detections"""

        

    @staticmethod    @staticmethod

    def bulk_create_from_detections(    def generate_infraction_code() -> str:

        detections: List[Dict[str, Any]],        """Generate unique infraction code"""

        device_id: Optional[str] = None,        from django.utils.crypto import get_random_string

        source: str = 'webcam_local'        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    ) -> List[Infraction]:        random = get_random_string(4, allowed_chars='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        """        return f"INF-{timestamp}-{random}"

        Create multiple infractions from detection data    

            @staticmethod

        Args:    @transaction.atomic

            detections: List of detection dictionaries with infraction data    def create_from_detection(

            device_id: Optional device UUID        detection_data: Dict,

            source: Source of detection        device_id: Optional[str] = None,

                    source: str = "webcam_local"

        Returns:    ) -> Optional[Infraction]:

            List of created Infraction objects        """

        """        Create infraction from detection data

        created_infractions = []        

                Args:

        # Get or create default device for webcam            detection_data: Dictionary with detection information

        device = None            device_id: Device UUID (optional, will use default if not provided)

        if device_id:            source: Source of detection (camera, webcam_local, etc)

            try:            

                device = Device.objects.get(id=device_id)        Returns:

            except Device.DoesNotExist:            Created Infraction instance or None if no infraction detected

                logger.warning(f"Device {device_id} not found")        """

                try:

        if not device:            # Extract detection info

            # Get or create default webcam device            vehicle_type = detection_data.get('class_name', 'car')

            device, _ = Device.objects.get_or_create(            confidence = detection_data.get('confidence', 0.0)

                code='WEBCAM_LOCAL',            bbox = detection_data.get('bbox', [])

                defaults={            license_plate = detection_data.get('license_plate')

                    'name': 'Webcam Local',            detected_speed = detection_data.get('speed')

                    'device_type': 'camera',            infraction_types = detection_data.get('infractions', [])

                    'status': 'active',            

                    'manufacturer': 'Local',            # If no infractions detected, don't create record

                    'model': 'Webcam',            if not infraction_types or len(infraction_types) == 0:

                }                logger.debug(f"No infractions detected for {vehicle_type}")

            )                return None

                    

        # Get or create default zone            # Get or create device

        zone, _ = Zone.objects.get_or_create(            device = None

            code='ZONE_TEST',            if device_id:

            defaults={                try:

                'name': 'Zona de Prueba',                    device = Device.objects.get(id=device_id)

                'zone_type': 'street',                except Device.DoesNotExist:

                'speed_limit': 60,                    logger.warning(f"Device {device_id} not found")

            }            

        )            # Use default device for webcam local if not specified

                    if not device:

        with transaction.atomic():                device, _ = Device.objects.get_or_create(

            for detection in detections:                    name="Webcam Local",

                try:                    defaults={

                    # Extract detection data                        "device_type": "webcam",

                    license_plate = detection.get('license_plate', '')                        "status": "active",

                    license_confidence = detection.get('ocr_confidence', 0.0)                        "ip_address": "127.0.0.1",

                    detected_speed = detection.get('speed')                        "is_active": True

                    infractions_list = detection.get('infractions', [])                    }

                                    )

                    if not infractions_list:            

                        continue            # Get or create default zone

                                zone, _ = Zone.objects.get_or_create(

                    # Get or create vehicle if license plate is detected                name="Zona Local",

                    vehicle = None                defaults={

                    if license_plate:                    "description": "Detección desde webcam local",

                        vehicle, created = Vehicle.objects.get_or_create(                    "speed_limit": 60

                            license_plate=license_plate,                }

                            defaults={            )

                                'vehicle_type': detection.get('class_name', 'car'),            

                                'status': 'active',            # Get the primary infraction type

                            }            primary_infraction = infraction_types[0] if infraction_types else 'other'

                        )            

                        if created:            # Map infraction types

                            logger.info(f"Created new vehicle: {license_plate}")            infraction_type_map = {

                                    'speeding': 'speed',

                    # Create infraction for each type detected                'speed': 'speed',

                    for infraction_type_name in infractions_list:                'red_light': 'red_light',

                        # Map detection infraction names to model choices                'wrong_lane': 'wrong_lane',

                        infraction_type_map = {                'no_helmet': 'no_helmet',

                            'speeding': 'speed',                'parking': 'parking',

                            'speed': 'speed',                'phone_use': 'phone_use',

                            'red_light': 'red_light',                'seatbelt': 'seatbelt',

                            'lane_invasion': 'wrong_lane',            }

                            'wrong_lane': 'wrong_lane',            

                            'no_helmet': 'no_helmet',            mapped_type = infraction_type_map.get(primary_infraction, 'other')

                            'parking': 'parking',            

                            'phone_use': 'phone_use',            # Determine severity

                            'seatbelt': 'seatbelt',            severity = 'medium'

                        }            if detected_speed:

                                        speed_over = detected_speed - zone.speed_limit

                        infraction_type = infraction_type_map.get(                if speed_over > 30:

                            infraction_type_name.lower(),                    severity = 'critical'

                            'other'                elif speed_over > 20:

                        )                    severity = 'high'

                                        elif speed_over > 10:

                        # Determine severity based on type and speed                    severity = 'medium'

                        severity = 'medium'                else:

                        if infraction_type == 'speed' and detected_speed:                    severity = 'low'

                            speed_limit = zone.speed_limit or 60            

                            excess = detected_speed - speed_limit            # Get or create vehicle if license plate detected

                            if excess > 40:            vehicle = None

                                severity = 'critical'            if license_plate:

                            elif excess > 20:                vehicle, created = Vehicle.objects.get_or_create(

                                severity = 'high'                    license_plate=license_plate,

                            elif excess > 10:                    defaults={

                                severity = 'medium'                        'vehicle_type': vehicle_type,

                            else:                        'make': 'Unknown',

                                severity = 'low'                        'model': 'Unknown'

                        elif infraction_type == 'red_light':                    }

                            severity = 'high'                )

                                        if created:

                        # Create the infraction                    logger.info(f"Created new vehicle record: {license_plate}")

                        infraction = Infraction.objects.create(            

                            infraction_type=infraction_type,            # Create infraction

                            severity=severity,            infraction = Infraction.objects.create(

                            device=device,                infraction_code=InfractionService.generate_infraction_code(),

                            zone=zone,                infraction_type=mapped_type,

                            vehicle=vehicle,                severity=severity,

                            license_plate_detected=license_plate,                device=device,

                            license_plate_confidence=license_confidence,                zone=zone,

                            detected_speed=detected_speed,                vehicle=vehicle,

                            speed_limit=zone.speed_limit,                license_plate_detected=license_plate or '',

                            status='pending',                license_plate_confidence=detection_data.get('ocr_confidence', 0.0),

                            detected_at=timezone.now(),                detected_speed=detected_speed,

                            evidence_metadata={                speed_limit=zone.speed_limit,

                                'source': source,                detected_at=timezone.now(),

                                'detection_confidence': detection.get('confidence', 0.0),                status='pending',

                                'bbox': detection.get('bbox', []),                evidence_metadata={

                                'vehicle_type': detection.get('class_name', 'unknown'),                    'source': source,

                            }                    'confidence': confidence,

                        )                    'bbox': bbox,

                                            'vehicle_type': vehicle_type,

                        # Create initial event                    'all_infractions': infraction_types,

                        InfractionEvent.objects.create(                    'detection_timestamp': timezone.now().isoformat()

                            infraction=infraction,                }

                            event_type='detected',            )

                            notes=f'Infraction detected by {source}',            

                            metadata={            logger.info(

                                'detection_data': detection,                f"Created infraction {infraction.infraction_code} - "

                                'source': source,                f"Type: {mapped_type}, Vehicle: {license_plate or 'Unknown'}, "

                            }                f"Severity: {severity}"

                        )            )

                                    

                        created_infractions.append(infraction)            return infraction

                                    

                        logger.info(        except Exception as e:

                            f"Created infraction {infraction.infraction_code}: "            logger.error(f"Error creating infraction from detection: {str(e)}", exc_info=True)

                            f"{infraction_type} for vehicle {license_plate or 'UNKNOWN'}"            return None

                        )    

                    @staticmethod

                except Exception as e:    def bulk_create_from_detections(

                    logger.error(f"Error creating infraction from detection: {str(e)}", exc_info=True)        detections: List[Dict],

                    # Continue with next detection        device_id: Optional[str] = None,

                    continue        source: str = "webcam_local"

            ) -> List[Infraction]:

        return created_infractions        """

            Create multiple infractions from detection list

    @staticmethod        

    def validate_infraction(infraction: Infraction, user, notes: str = '') -> bool:        Args:

        """            detections: List of detection dictionaries

        Validate an infraction            device_id: Device UUID (optional)

                    source: Source of detections

        Args:            

            infraction: Infraction object to validate        Returns:

            user: User performing validation            List of created Infraction instances

            notes: Optional validation notes        """

                    infractions = []

        Returns:        

            True if validated successfully        for detection in detections:

        """            infraction = InfractionService.create_from_detection(

        try:                detection_data=detection,

            with transaction.atomic():                device_id=device_id,

                infraction.status = 'validated'                source=source

                infraction.reviewed_by = user            )

                infraction.reviewed_at = timezone.now()            if infraction:

                infraction.review_notes = notes                infractions.append(infraction)

                infraction.save()        

                        logger.info(f"Created {len(infractions)} infractions from {len(detections)} detections")

                # Create event        

                InfractionEvent.objects.create(        return infractions

                    infraction=infraction,
                    event_type='validated',
                    user=user,
                    notes=notes or 'Infraction validated'
                )
                
                logger.info(f"Infraction {infraction.infraction_code} validated by {user}")
                return True
                
        except Exception as e:
            logger.error(f"Error validating infraction: {str(e)}", exc_info=True)
            return False
    
    @staticmethod
    def reject_infraction(infraction: Infraction, user, notes: str = '') -> bool:
        """
        Reject an infraction
        
        Args:
            infraction: Infraction object to reject
            user: User performing rejection
            notes: Rejection reason
            
        Returns:
            True if rejected successfully
        """
        try:
            with transaction.atomic():
                infraction.status = 'rejected'
                infraction.reviewed_by = user
                infraction.reviewed_at = timezone.now()
                infraction.review_notes = notes
                infraction.save()
                
                # Create event
                InfractionEvent.objects.create(
                    infraction=infraction,
                    event_type='rejected',
                    user=user,
                    notes=notes or 'Infraction rejected'
                )
                
                logger.info(f"Infraction {infraction.infraction_code} rejected by {user}")
                return True
                
        except Exception as e:
            logger.error(f"Error rejecting infraction: {str(e)}", exc_info=True)
            return False

