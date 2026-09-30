"""
`route_template`, the `route` field on every `http_request` log line.

The scopes are built by hand, shaped like what FastAPI leaves behind: cv-core
does not depend on FastAPI, and the consumers' request-logging tests cover the
real app.
"""

from types import SimpleNamespace

import pytest
from starlette.requests import Request

from cv_core.correlation_middleware import route_template


def _request(**scope) -> Request:
    return Request({"type": "http", "method": "GET", "path": "/", "headers": [], **scope})


@pytest.mark.unit
class TestRouteTemplate:
    def test_an_included_route_logs_its_prefixed_path(self):
        # FastAPI >= 0.137: scope["route"] is the sub-router's route, unprefixed
        request = _request(
            route=SimpleNamespace(path="/teams/"),
            fastapi={"effective_route_context": SimpleNamespace(path="/v1/internal/teams/")},
        )
        assert route_template(request) == "/v1/internal/teams/"

    def test_a_route_on_the_app_itself_logs_its_path(self):
        assert route_template(_request(route=SimpleNamespace(path="/ping"))) == "/ping"

    def test_a_fastapi_scope_without_a_context_falls_back_to_the_route(self):
        request = _request(route=SimpleNamespace(path="/ping"), fastapi={})
        assert route_template(request) == "/ping"

    def test_an_unmatched_request_has_no_template(self):
        assert route_template(_request()) is None
