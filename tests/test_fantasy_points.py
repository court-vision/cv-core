"""
The formula, pinned against itself written out longhand.

`calculate_fantasy_points` reads `DEFAULT_POINT_WEIGHTS`; asserting the two
agree with each other would be circular. These tests write the formula
literally — the sum five hand-written copies used to compute — so a change to
the weight table breaks a test instead of silently changing every stored
`fpts` value.
"""

import pytest

from cv_core.transformers import calculate_fantasy_points


def literal_formula(s: dict) -> int:
    return int(
        s["pts"] + s["reb"] + 2 * s["ast"] + 4 * (s["stl"] + s["blk"])
        - 2 * s["tov"] + s["fg3m"] + (2 * s["fgm"] - s["fga"]) + (s["ftm"] - s["fta"])
    )


LINES = [
    # a big night
    dict(pts=42, reb=12, ast=9, stl=3, blk=2, tov=4, fgm=16, fga=28, fg3m=5, ftm=5, fta=6),
    # a negative total (heavy turnovers, awful shooting)
    dict(pts=2, reb=1, ast=0, stl=0, blk=0, tov=7, fgm=1, fga=14, fg3m=0, ftm=0, fta=4),
    # all zeros
    dict(pts=0, reb=0, ast=0, stl=0, blk=0, tov=0, fgm=0, fga=0, fg3m=0, ftm=0, fta=0),
    # free-throw-only line
    dict(pts=11, reb=0, ast=0, stl=0, blk=0, tov=0, fgm=0, fga=0, fg3m=0, ftm=11, fta=12),
]


@pytest.mark.unit
@pytest.mark.parametrize("line", LINES)
def test_matches_the_literal_formula(line):
    assert calculate_fantasy_points(line) == literal_formula(line)


@pytest.mark.unit
def test_negative_totals_truncate_like_int():
    line = LINES[1]
    assert literal_formula(line) < 0
    # int() truncates toward zero; the sum is integer-valued so this is exact
    assert calculate_fantasy_points(line) == literal_formula(line)
