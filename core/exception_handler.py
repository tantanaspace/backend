from django.http import Http404
from rest_framework.exceptions import ErrorDetail
from rest_framework.serializers import as_serializer_error
from rest_framework.views import exception_handler


def make_pretty_error(data, errors):
    for error in errors:
        if isinstance(errors[error], dict) and len(errors[error]) >= 1:
            for er in errors[error]:
                make_pretty_error(data, {er: errors[error][er]})
        elif isinstance(errors[error], list) and isinstance(
            errors[error][0], ErrorDetail
        ):
            for i, _ in enumerate(errors[error]):
                data["errors"].append(
                    {
                        "error": f"{error}_{errors[error][0].code}",
                        "message": errors[error][i],
                    }
                )
        elif isinstance(errors[error][0], dict) and len(errors[error]) >= 1:
            for er in errors[error]:
                make_pretty_error(data, er)
        else:
            data["errors"].append(
                {"error": f"{error}_{errors[error].code}", "message": errors[error]}
            )


def _handle_validation_error(exc, context):
    response = exception_handler(exc, context)
    errors = as_serializer_error(exc)

    if response is not None:
        response.data = {"status_code": response.status_code, "errors": []}
        make_pretty_error(response.data, errors)
    return response


def _handle_django_exception(exc, context):
    response = exception_handler(exc, context)
    errors = response.data
    if isinstance(exc, Http404):
        response.data = {"status_code": response.status_code, "errors": []}
        make_pretty_error(response.data, errors)
        return response
    return response


def _handle_common_exception(exc, context):
    response = exception_handler(exc, context)
    errors = response.data
    response.data = {"status_code": response.status_code, "errors": []}
    make_pretty_error(response.data, errors)
    return response


def custom_exception_handler(exc, context):
    handlers = {
        "ValidationError": _handle_validation_error,
        "Http404": _handle_django_exception,
        "Throttled": _handle_common_exception,
        "AuthenticationFailed": _handle_common_exception,
        "NotFound": _handle_common_exception,
        "NotAuthenticated": _handle_common_exception,
    }
    response = exception_handler(exc, context)

    exception_class = exc.__class__.__name__
    if exception_class in handlers:
        return handlers[exception_class](exc, context)
    return response
