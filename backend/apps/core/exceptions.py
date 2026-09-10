from rest_framework.views import exception_handler as drf_exception_handler


def exception_handler(exc, context):
    response = drf_exception_handler(exc, context)
    if response is None:
        return None
    detail = response.data
    error = detail if isinstance(detail, str) else "request_failed"
    response.data = {"error": error, "detail": detail}
    return response
