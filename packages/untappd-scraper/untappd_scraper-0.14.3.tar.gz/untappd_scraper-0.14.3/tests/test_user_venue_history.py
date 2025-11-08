"""Test user venue history scraping."""

from __future__ import annotations

import pytest
from untappd_scraper.user_venue_history import load_user_venue_history
from utpd_models_web.constants import UNTAPPD_VENUE_HISTORY_SIZE

# ----- Tests -----


@pytest.mark.usefixtures("_mock_user_venue_history_get")
def test_load_user_venue_history() -> None:
    venues = load_user_venue_history("test")
    assert len(venues) == UNTAPPD_VENUE_HISTORY_SIZE

    result = venues[0]

    assert result.name
    assert result.url


@pytest.mark.webtest
@pytest.mark.parametrize(
    "venue_id, expected",
    [
        (14705, False),  # 4 pines
        (107565, True),  # sweeney's
    ],
)
def test_recent_venue_verified(venue_id: int, expected: bool) -> None:
    venues = load_user_venue_history("mw1414")
    assert len(venues) == UNTAPPD_VENUE_HISTORY_SIZE

    result = next((v for v in venues if v.venue_id == venue_id), None)

    assert result
    assert result.is_verified == expected
