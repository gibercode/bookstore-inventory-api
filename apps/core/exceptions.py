from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    """Return every API error with the same envelope: {"error": {...}}."""
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
