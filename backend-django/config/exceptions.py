"""
Custom exception handler for DRF
"""
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """
    Custom exception handler that adds standardized error format
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)

    if response is not None:
        # Standardize error response format
        custom_response_data = {
            'success': False,
            'error': {
                'code': getattr(exc, 'default_code', 'error'),
                'message': str(exc),
                'details': response.data if isinstance(response.data, dict) else {'detail': response.data}
            }
        }
        response.data = custom_response_data

    return response


class ServiceUnavailableException(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = 'Service temporarily unavailable, please try again later.'
    default_code = 'service_unavailable'


class InvalidCredentialsException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'Invalid credentials provided.'
    default_code = 'invalid_credentials'


class ResourceNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Resource not found.'
    default_code = 'resource_not_found'
