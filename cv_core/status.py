"""
The API status vocabulary shared by both services' response envelopes.

Lifted from `schemas/common.py`, where the two repos' copies had drifted by one
member: only data-platform used SKIPPED (a pipeline run that never started
because another held the execution lock). This is the superset — the backend
simply never emits SKIPPED, which is harmless for a str enum.
"""

from enum import Enum


class ApiStatus(str, Enum):
    """Standard API response statuses"""

    SUCCESS = "success"
    ERROR = "error"
    SKIPPED = "skipped"
    BAD_REQUEST = "bad_request"
    VALIDATION_ERROR = "validation_error"
    AUTHENTICATION_ERROR = "authentication_error"
    AUTHORIZATION_ERROR = "authorization_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    RATE_LIMITED = "rate_limited"
    SERVER_ERROR = "server_error"
