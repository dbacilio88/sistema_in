"""
License plate recognition module.

This module provides classes and utilities for detecting and reading
license plates from vehicle images using EasyOCR with Peru-specific
validation and formatting.
"""

from .plate_detector import LicensePlateDetector
from .plate_reader import LicensePlateReader
from .plate_validator import PeruvianPlateValidator, PlateFormat

__all__ = [
    "LicensePlateDetector", 
    "LicensePlateReader", 
    "PeruvianPlateValidator", 
    "PlateFormat"
]