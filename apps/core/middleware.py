from django.conf import settings
from django.http import JsonResponse

NOT_FOUND = 'Not found.'
SERVER_ERROR = 'Internal server error.'


class JsonErrorMiddleware:
    """Return the API error envelope for 404/500 responses under /api/.

    Django answers unmatched URLs and unhandled exceptions with HTML, which
    DRF's exception handler never sees. In DEBUG the 500 page is left alone
    so the traceback stays visible.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.prefix = f'/{settings.API_PREFIX}/'

    def __call__(self, request):
        response = self.get_response(request)

        if not request.path.startswith(self.prefix):
            return response
        if 'text/html' not in response.get('Content-Type', ''):
            return response

        if response.status_code == 404:
            return self._error(404, NOT_FOUND)
        if response.status_code == 500 and not settings.DEBUG:
            return self._error(500, SERVER_ERROR)
        return response

    @staticmethod
    def _error(status_code, detail):
        return JsonResponse(
            {'error': {'status_code': status_code, 'detail': detail}},
            status=status_code,
        )
