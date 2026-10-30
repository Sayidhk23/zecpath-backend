import logging

logger = logging.getLogger(__name__)

class APISecurityMiddleware:
    def __init__(self, get_response):
        self.get_response= get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            logger.info(
                "API request: method=%s path=%s",
                request.method,
                request.path
            )
        response = self.get_response(request)

        if(
            request.path.startswith('/api/')
            and response.status_code in [401, 403]
        ):
            logger.warning(
                "Access denied: method=%s path=%s status=%s",
                request.method,
                request.path,
                response.status_code
            )

        return response