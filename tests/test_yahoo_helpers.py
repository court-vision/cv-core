"""
The Yahoo team-abbreviation map is canonical: nba.teams keys, not ESPN forms.

The two repos' copies of this map disagreed for a season — backend normalized
Philadelphia/Phoenix to PHI/PHX (the `nba.teams` primary keys) while
data-platform's dead copy normalized to ESPN's PHL/PHO. This is the backend
copy, promoted; these tests pin the direction so the drift cannot recur.
"""

import pytest

from cv_core.yahoo_helpers import YAHOO_TEAM_MAP

# The 30 canonical abbreviations seeded into nba.teams by both repos.
CANONICAL = {
    "ATL", "BOS", "BKN", "CHA", "CHI", "CLE", "DAL", "DEN", "DET", "GSW",
    "HOU", "IND", "LAC", "LAL", "MEM", "MIA", "MIL", "MIN", "NOP", "NYK",
    "OKC", "ORL", "PHI", "PHX", "POR", "SAC", "SAS", "TOR", "UTA", "WAS",
}


@pytest.mark.unit
class TestCanonicalDirection:
    def test_espn_forms_normalize_to_canonical(self):
        assert YAHOO_TEAM_MAP["PHL"] == "PHI"
        assert YAHOO_TEAM_MAP["PHO"] == "PHX"

    def test_canonical_forms_are_fixed_points(self):
        assert YAHOO_TEAM_MAP["PHI"] == "PHI"
        assert YAHOO_TEAM_MAP["PHX"] == "PHX"

    def test_every_value_is_a_canonical_abbreviation(self):
        stray = {v for v in YAHOO_TEAM_MAP.values()} - CANONICAL
        assert not stray, f"map emits non-canonical abbreviations: {stray}"
