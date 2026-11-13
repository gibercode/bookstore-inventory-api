from django.db import InterfaceError, OperationalError
from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


class ConflictError(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'The request conflicts with the current state of the resource.'
    default_code = 'conflict'


def custom_exception_handler(exc, context):
    """Return every API error with the same envelope: {"error": {...}}."""
    if isinstance(exc, (OperationalError, InterfaceError)):
        return Response(
            {'error': {'status_code': 503, 'detail': 'Service temporarily unavailable.'}},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    response = exception_handler(exc, context)
    if response is None:
        return None

    detail = response.data
    if isinstance(detail, dict) and set(detail) == {'detail'}:
        detail = detail['detail']

    response.data = {
        'error': {
            'status_code': response.status_code,
            'detail': detail,
        }
    }
    return response

