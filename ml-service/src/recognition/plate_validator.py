"""
Peruvian License Plate Validator.

This module provides validation for Peruvian license plate formats
and related utilities for format detection and correction.
"""

import re
import logging
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class PlateFormat(Enum):
    """Peruvian license plate format types."""
    OLD_STANDARD = "old_standard"      # ABC-123 (3 letters + 3 numbers)
    NEW_STANDARD = "new_standard"      # ABC-1234 (3 letters + 4 numbers)  
    TAXI = "taxi"                      # T1A-123 (T + number + letter + 3 numbers)
    MOTORCYCLE = "motorcycle"          # A1-123 (letter + number + 3 numbers)
    COMMERCIAL = "commercial"          # AB-1234 (2 letters + 4 numbers)
    POLICE = "police"                  # PNP-123 (special police format)
    DIPLOMATIC = "diplomatic"          # CD-123 (diplomatic corps)
    TEMPORARY = "temporary"            # TP-123 (temporary plates)
    UNKNOWN = "unknown"

@dataclass
class ValidationResult:
    """License plate validation result."""
    is_valid: bool
    format_type: PlateFormat
    confidence: float
    corrected_text: Optional[str] = None
    errors: List[str] = None

class PeruvianPlateValidator:
    """
    Validator for Peruvian license plate formats.
    
    Validates plates according to official Peruvian standards:
    - Old format: ABC-123 (until 2016)
    - New format: ABC-1234 (from 2016)
    - Special formats: Taxi, motorcycle, commercial, etc.
    """
    
    def __init__(self):
        """Initialize validator with Peruvian plate patterns."""
        self.patterns = {
            PlateFormat.OLD_STANDARD: {
                'pattern': r'^[A-Z]{3}-?[0-9]{3}$',
                'description': 'Old standard format: ABC-123',
                'example': 'ABC-123',
                'active_period': '1969-2016'
            },
            PlateFormat.NEW_STANDARD: {
                'pattern': r'^[A-Z]{3}-?[0-9]{4}$',
                'description': 'New standard format: ABC-1234',
                'example': 'ABC-1234',
                'active_period': '2016-present'
            },
            PlateFormat.TAXI: {
                'pattern': r'^T[0-9][A-Z]-?[0-9]{3}$',
                'description': 'Taxi format: T1A-123',
                'example': 'T1A-123',
                'active_period': '2010-present'
            },
            PlateFormat.MOTORCYCLE: {
                'pattern': r'^[A-Z][0-9]-?[0-9]{3}$',
                'description': 'Motorcycle format: A1-123',
                'example': 'A1-123',
                'active_period': '2000-present'
            },
            PlateFormat.COMMERCIAL: {
                'pattern': r'^[A-Z]{2}-?[0-9]{4}$',
                'description': 'Commercial format: AB-1234',
                'example': 'AB-1234',
                'active_period': '2015-present'
            },
            PlateFormat.POLICE: {
                'pattern': r'^PNP-?[0-9]{3,4}$',
                'description': 'Police format: PNP-123',
                'example': 'PNP-123',
                'active_period': '1990-present'
            },
            PlateFormat.DIPLOMATIC: {
                'pattern': r'^CD-?[0-9]{3,4}$',
                'description': 'Diplomatic format: CD-123',
                'example': 'CD-123',
                'active_period': '1980-present'
            },
            PlateFormat.TEMPORARY: {
                'pattern': r'^TP-?[0-9]{3,4}$',
                'description': 'Temporary format: TP-123',
                'example': 'TP-123',
                'active_period': '2010-present'
            }
        }
        
        # Forbidden letter combinations (to avoid offensive words)
        self.forbidden_combinations = {
            'WTF', 'ASS', 'SEX', 'GAY', 'HIV', 'AIDS', 'KKK',
            'FUK', 'FCK', 'SHT', 'DMN', 'HLL', 'DIE', 'KIL'
        }
        
        # Reserved prefixes for special vehicles
        self.reserved_prefixes = {
            'PNP': 'Police Nacional del Peru',
            'EJE': 'Ejercito del Peru', 
            'FAP': 'Fuerza Aerea del Peru',
            'MGP': 'Marina de Guerra del Peru',
            'CD': 'Cuerpo Diplomatico',
            'CC': 'Cuerpo Consular',
            'TP': 'Placa Temporal'
        }
        
        logger.info("PeruvianPlateValidator initialized")
    
    def validate(self, plate_text: str) -> ValidationResult:
        """
        Validate license plate text against Peruvian formats.
        
        Args:
            plate_text: License plate text to validate
            
        Returns:
            ValidationResult with validation details
        """
        if not plate_text:
            return ValidationResult(
                is_valid=False,
                format_type=PlateFormat.UNKNOWN,
                confidence=0.0,
                errors=["Empty plate text"]
            )
        
        # Clean and normalize input
        normalized = self._normalize_plate_text(plate_text)
        
        # Try exact pattern matching first
        for format_type, pattern_info in self.patterns.items():
            if re.match(pattern_info['pattern'], normalized):
                confidence = self._calculate_confidence(normalized, format_type)
                
                # Check for forbidden combinations
                errors = self._check_forbidden_combinations(normalized)
                is_valid = len(errors) == 0
                
                return ValidationResult(
                    is_valid=is_valid,
                    format_type=format_type,
                    confidence=confidence,
                    corrected_text=normalized,
                    errors=errors
                )
        
        # Try fuzzy matching for OCR errors
        best_match = self._fuzzy_validate(normalized)
        if best_match:
            return best_match
        
        # No valid format found
        return ValidationResult(
            is_valid=False,
            format_type=PlateFormat.UNKNOWN,
            confidence=0.0,
            errors=[f"Does not match any valid Peruvian plate format: {normalized}"]
        )
    
    def _normalize_plate_text(self, text: str) -> str:
        """Normalize plate text for validation."""
        # Convert to uppercase
        normalized = text.upper().strip()
        
        # Remove extra spaces and special characters
        normalized = re.sub(r'[^A-Z0-9-]', '', normalized)
        
        # Standardize dash placement based on length and content
        if '-' not in normalized:
            # Add dash in standard position based on format detection
            if len(normalized) == 6:
                # ABC123 -> ABC-123
                if normalized[:3].isalpha() and normalized[3:].isdigit():
                    normalized = normalized[:3] + '-' + normalized[3:]
                # A1123 -> A1-123 (motorcycle)
                elif normalized[0].isalpha() and normalized[1].isdigit() and normalized[2:].isdigit():
                    normalized = normalized[:2] + '-' + normalized[2:]
            elif len(normalized) == 7:
                # ABC1234 -> ABC-1234
                if normalized[:3].isalpha() and normalized[3:].isdigit():
                    normalized = normalized[:3] + '-' + normalized[3:]
                # T1A123 -> T1A-123 (taxi)
                elif normalized[0] == 'T' and normalized[1].isdigit() and normalized[2].isalpha():
                    normalized = normalized[:3] + '-' + normalized[3:]
        
        return normalized
    
    def _calculate_confidence(self, text: str, format_type: PlateFormat) -> float:
        """Calculate confidence score for format match."""
        base_confidence = 0.9  # Base confidence for pattern match
        
        # Adjust based on format likelihood
        format_weights = {
            PlateFormat.NEW_STANDARD: 1.0,    # Most common current format
            PlateFormat.OLD_STANDARD: 0.8,    # Still valid but older
            PlateFormat.TAXI: 0.9,            # Common for taxis
            PlateFormat.MOTORCYCLE: 0.85,     # Common for motorcycles
            PlateFormat.COMMERCIAL: 0.75,     # Less common
            PlateFormat.POLICE: 0.95,         # Distinctive format
            PlateFormat.DIPLOMATIC: 0.9,      # Distinctive format
            PlateFormat.TEMPORARY: 0.7        # Temporary only
        }
        
        weight = format_weights.get(format_type, 0.5)
        
        # Penalize forbidden combinations
        if self._has_forbidden_combination(text):
            weight *= 0.3
        
        return base_confidence * weight
    
    def _check_forbidden_combinations(self, text: str) -> List[str]:
        """Check for forbidden letter combinations."""
        errors = []
        
        # Remove dash and check for forbidden sequences
        clean_text = text.replace('-', '')
        
        for forbidden in self.forbidden_combinations:
            if forbidden in clean_text:
                errors.append(f"Contains forbidden combination: {forbidden}")
        
        return errors
    
    def _has_forbidden_combination(self, text: str) -> bool:
        """Check if text has forbidden combinations."""
        clean_text = text.replace('-', '')
        return any(forbidden in clean_text for forbidden in self.forbidden_combinations)
    
    def _fuzzy_validate(self, text: str) -> Optional[ValidationResult]:
        """Attempt fuzzy validation for OCR errors."""
        # Try common OCR substitutions
        substitutions = [
            ('0', 'O'), ('O', '0'),
            ('1', 'I'), ('I', '1'),
            ('5', 'S'), ('S', '5'),
            ('8', 'B'), ('B', '8'),
            ('6', 'G'), ('G', '6'),
            ('2', 'Z'), ('Z', '2')
        ]
        
        candidates = [text]
        
        # Generate candidates with single substitutions
        for old_char, new_char in substitutions:
            if old_char in text:
                candidate = text.replace(old_char, new_char, 1)
                candidates.append(candidate)
        
        # Test each candidate
        best_result = None
        best_confidence = 0.0
        
        for candidate in candidates:
            for format_type, pattern_info in self.patterns.items():
                if re.match(pattern_info['pattern'], candidate):
                    confidence = self._calculate_confidence(candidate, format_type) * 0.8  # Penalty for correction
                    
                    if confidence > best_confidence:
                        errors = self._check_forbidden_combinations(candidate)
                        best_result = ValidationResult(
                            is_valid=len(errors) == 0,
                            format_type=format_type,
                            confidence=confidence,
                            corrected_text=candidate,
                            errors=errors
                        )
                        best_confidence = confidence
        
        return best_result
    
    def get_format_info(self, format_type: PlateFormat) -> Dict[str, Any]:
        """Get information about a specific plate format."""
        if format_type in self.patterns:
            return self.patterns[format_type].copy()
        return {}
    
    def get_all_formats(self) -> Dict[PlateFormat, Dict[str, Any]]:
        """Get information about all supported formats."""
        return self.patterns.copy()
    
    def is_reserved_prefix(self, text: str) -> Tuple[bool, Optional[str]]:
        """Check if plate has reserved prefix."""
        clean_text = text.replace('-', '')
        
        for prefix, description in self.reserved_prefixes.items():
            if clean_text.startswith(prefix):
                return True, description
        
        return False, None
    
    def suggest_corrections(self, text: str) -> List[str]:
        """Suggest possible corrections for invalid plate text."""
        suggestions = []
        
        if not text:
            return suggestions
        
        normalized = self._normalize_plate_text(text)
        
        # Try common OCR corrections
        corrections = [
            ('0', 'O'), ('O', '0'),
            ('1', 'I'), ('I', '1'), ('1', 'L'),
            ('5', 'S'), ('S', '5'),
            ('8', 'B'), ('B', '8'),
            ('6', 'G'), ('G', '6'),
            ('2', 'Z'), ('Z', '2'),
            ('4', 'A'), ('A', '4')
        ]
        
        for old_char, new_char in corrections:
            if old_char in normalized:
                suggestion = normalized.replace(old_char, new_char)
                validation = self.validate(suggestion)
                if validation.is_valid:
                    suggestions.append(suggestion)
        
        # Try different dash positions
        no_dash = normalized.replace('-', '')
        for i in range(1, len(no_dash)):
            suggestion = no_dash[:i] + '-' + no_dash[i:]
            validation = self.validate(suggestion)
            if validation.is_valid:
                suggestions.append(suggestion)
        
        # Remove duplicates and sort by likelihood
        unique_suggestions = list(set(suggestions))
        
        # Sort by validation confidence
        unique_suggestions.sort(key=lambda x: self.validate(x).confidence, reverse=True)
        
        return unique_suggestions[:5]  # Return top 5 suggestions
    
    def get_validation_stats(self) -> Dict[str, Any]:
        """Get validator statistics and configuration."""
        return {
            "supported_formats": len(self.patterns),
            "format_types": [f.value for f in self.patterns.keys()],
            "forbidden_combinations_count": len(self.forbidden_combinations),
            "reserved_prefixes_count": len(self.reserved_prefixes),
            "active_formats": [
                f.value for f, info in self.patterns.items() 
                if 'present' in info['active_period']
            ]
        }