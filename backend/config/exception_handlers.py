from rest_framework import status
from rest_framework.views import exception_handler


ERROR_CODE_BY_STATUS = {
    status.HTTP_400_BAD_REQUEST: 'validation_error',
    status.HTTP_401_UNAUTHORIZED: 'authentication_failed',
    status.HTTP_403_FORBIDDEN: 'permission_denied',
    status.HTTP_404_NOT_FOUND: 'not_found',
    status.HTTP_409_CONFLICT: 'conflict',
    status.HTTP_429_TOO_MANY_REQUESTS: 'rate_limit_exceeded',
    status.HTTP_500_INTERNAL_SERVER_ERROR: 'internal_server_error',
}


def standard_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is None:
        return response

    original_data = response.data
    message = 'Invalid request.'
    details = {}

    if isinstance(original_data, dict):
        if 'detail' in original_data:
            message = str(original_data['detail'])
        else:
            details = original_data
    else:
        details = {'non_field_errors': original_data}

    response.data = {
        'error_code': ERROR_CODE_BY_STATUS.get(
            response.status_code,
            'internal_server_error',
        ),
        'message': message,
        'details': details,
    }
    return response
