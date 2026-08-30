"""
cv-core — utilities shared by the Court Vision backend and data-platform.

Everything here is pure with respect to the services: no database, no
settings object, no FastAPI app. What is deliberately NOT here (and why) is
recorded in the README — in short: Peewee models (they bind to each repo's
own db runtime), credential_service (imports models), extractors (drifted
forks), and each service's settings/db/health/middleware (deliberately
different). Those stay duplicated under data-platform's mirror-drift guard
until a v2 tackles them.
"""

__all__ = [
    "correlation_middleware",
    "crypto",
    "errors",
    "logging",
    "nba_calendar",
    "resilience",
    "scoring_vocab",
    "season",
    "status",
    "transformers",
    "yahoo_helpers",
]
