import traceback

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):

    response = exception_handler(exc, context)

    if response is not None:
        data = response.data

        if isinstance(data, dict):
            message = data.get("detail")

            if message is None:
                message = "Request validation failed."

            errors = None if "detail" in data else data

        else:
            message = "Request failed."
            errors = data

        return Response(
            {
                "success": False,
                "status_code": response.status_code,
                "message": str(message),
                "errors": errors,
            },
            status=response.status_code,
        )

    # TEMPORARY DEBUGGING: print the actual exception.
    print("\n========== ATS API EXCEPTION ==========")
    traceback.print_exception(type(exc), exc, exc.__traceback__)
    print("========================================\n")

    return Response(
        {
            "success": False,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Internal server error.",
            "errors": None,
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )