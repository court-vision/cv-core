"""
Fantasy Points Transformer

The house fantasy-points formula, applied to a stat line. The weights live in
`cv_core.scoring_vocab.DEFAULT_POINT_WEIGHTS` — this function is that table
folded over a box score, so there is exactly one place the formula exists.

The `int()` truncation is load-bearing: every `fpts` column ever written used
it, and the weights are exact binary floats over integer stats, so the sum is
exact and truncation is deterministic. Changing it would change stored data.

This file replaced five hand-copied versions of the same sum across two repos
(PRODUCTION_READINESS item 5); a parity test pins it against the literal
formula so the weight table cannot drift from what the copies computed.
"""

from typing import TypedDict, Union

from cv_core.scoring_vocab import DEFAULT_POINT_WEIGHTS


class PlayerStats(TypedDict):
    """Type definition for player stats used in fantasy point calculation."""

    pts: int
    reb: int
    ast: int
    stl: int
    blk: int
    tov: int
    fgm: int
    fga: int
    fg3m: int
    ftm: int
    fta: int


def calculate_fantasy_points(stats: PlayerStats) -> int:
    """The default formula: pts + reb + 2*ast + 4*(stl+blk) - 2*tov + fg3m + (2*fgm - fga) + (ftm - fta)."""
    return int(sum(stats[key] * weight for key, weight in DEFAULT_POINT_WEIGHTS.items()))


def minutes_to_int(min_str: Union[str, int, float, None]) -> int:
    """
    Convert minutes to an integer from various formats.

    Handles:
    - ISO 8601 duration "PT34M56.00S" -> 34  (nba_api live BoxScore format)
    - String "34:56" -> 34                    (nba_api stats format)
    - Float 34.5 -> 34
    - Int 34 -> 34
    - None -> 0

    Args:
        min_str: Minutes value in various formats

    Returns:
        Integer minutes (truncated, not rounded)

    Examples:
        >>> minutes_to_int("PT34M56.00S")
        34
        >>> minutes_to_int("34:56")
        34
        >>> minutes_to_int(34.5)
        34
        >>> minutes_to_int(None)
        0
    """
    import re

    if min_str is None:
        return 0

    if isinstance(min_str, (int, float)):
        return int(min_str)

    s = str(min_str)

    # ISO 8601 duration format: "PT18M00.00S" (from nba_api live BoxScore)
    if s.startswith("PT"):
        match = re.match(r"PT(\d+)M", s)
        if match:
            return int(match.group(1))
        return 0

    # MM:SS format: "34:56" (from nba_api stats endpoints)
    if ":" in s:
        parts = s.split(":")
        return int(parts[0])

    try:
        return int(min_str)
    except (ValueError, TypeError):
        return 0
