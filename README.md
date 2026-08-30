# cv-core

Shared utilities for the Court Vision backend and data-platform. Before this
package, 9,000+ lines were duplicated between the two repos and ~1,000 of them
had already drifted — including a fantasy-points formula that existed in five
copies and an NBA-day rule open-coded ~20 times in two timezones
(`docs/PRODUCTION_READINESS.md` item 5).

## What's here (v1)

| Module | What |
|---|---|
| `cv_core.nba_calendar` | The NBA game date: one rule (6 AM Eastern), one definition |
| `cv_core.season` | Season keys ("2026-27"), derivation and validation |
| `cv_core.status` | `ApiStatus` — the response-envelope status vocabulary |
| `cv_core.errors` | Error codes and the error-envelope helpers |
| `cv_core.logging` | structlog setup, `get_logger`, correlation-id contextvars |
| `cv_core.correlation_middleware` | X-Correlation-ID Starlette middleware |
| `cv_core.crypto` | Fernet envelope encryption for stored provider credentials |
| `cv_core.resilience` | `@with_retry`, circuit breakers, `ResilientHTTPClient` |
| `cv_core.scoring_vocab` | Canonical stat vocabulary, provider stat-id maps, `DEFAULT_POINT_WEIGHTS`, standard 9-cat |
| `cv_core.transformers` | `calculate_fantasy_points` (the weight table folded over a box score — the one copy), `normalize_name`, `minutes_to_int` |
| `cv_core.yahoo_helpers` | Yahoo team-key parsing and the team-abbreviation map (canonical `PHI`/`PHX`) |

## What's deliberately NOT here

- **Peewee models** — every model inherits each repo's own `db.base.BaseModel`,
  and the two repos' DB runtimes are genuinely different (bounded executor +
  `run_db` in backend; `run_in_db_thread` in data-platform). Sharing models
  needs a `DatabaseProxy` refactor → v2.
- **`credential_service`** — imports the models.
- **Extractors** — the backend's copies are stale forks of data-platform's;
  reconcile before sharing.
- **`settings`, `db/base`, `health`, `middleware`** — deliberately different
  per service.
- The remaining byte-identical duplicates (models, extractor bases, misc) are
  watched by `data-platform/scripts/check_backend_mirror.py`, which fails when
  they drift.

## Consuming

Both services pin an exact release tag by tarball URL (public repo — no auth,
no git binary needed in Docker builds; `railway up` tarballs a single-repo
checkout, so path dependencies are impossible):

```
cv-core @ https://github.com/court-vision/cv-core/archive/refs/tags/v0.1.0.tar.gz
```

## Releasing

1. PR into `main` here; CI must pass (pytest on 3.12 and 3.13).
2. Tag: `git tag v0.x.y && git push origin v0.x.y`.
3. Bump the pin in each consumer's `requirements.txt` (separate PRs; either
   order — v1 modules carry no cross-service wire contract).

Consumers pin exact tags, never a branch. One rule with teeth: the
`cryptography` floor here and the `==` pins in **both** consumers must move
together — the two services decrypt the same `usr.provider_connections` rows.

## The `int()` in `calculate_fantasy_points`

Load-bearing. Every `fpts` column ever written truncated; the weights are
exact binary floats over integer stats, so the sum is exact and truncation is
deterministic. `tests/test_fantasy_points.py` pins the function against the
literal formula — not against the weight table it reads — so the table cannot
drift from what five hand-written copies used to compute.
