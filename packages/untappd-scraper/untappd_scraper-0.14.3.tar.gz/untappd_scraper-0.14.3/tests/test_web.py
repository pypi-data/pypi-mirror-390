"""Test web utils."""

from __future__ import annotations

import pytest
from untappd_scraper.web import url_of
from utpd_models_web.constants import UNTAPPD_BASE_URL


@pytest.mark.parametrize(
    "user_id, venue_id, brewery_id, beer_id, search, page, query, expected",
    [
        ("", "", "", "", False, "", None, f"{UNTAPPD_BASE_URL.rstrip('/')}"),
        ("123", "", "", "", False, "", None, f"{UNTAPPD_BASE_URL}user/123"),
        ("", "456", "", "", False, "", None, f"{UNTAPPD_BASE_URL}venue/456"),
        ("", "", "789", "", False, "", None, f"{UNTAPPD_BASE_URL}brewery/789"),
        ("", "", "", "101112", False, "", None, f"{UNTAPPD_BASE_URL}beer/101112"),
        ("", "", "", "", True, "", None, f"{UNTAPPD_BASE_URL}search"),
        ("", "", "", "", False, "page1", None, f"{UNTAPPD_BASE_URL}page1"),
        ("", "", "", "", False, "/v/page1", None, f"{UNTAPPD_BASE_URL}v/page1"),
        ("", "", "", "", False, "", {"key": "val"}, f"{UNTAPPD_BASE_URL.rstrip('/')}?key=val"),
    ],
)
def test_url_of(
    user_id: str,
    venue_id: str,
    brewery_id: str,
    beer_id: str,
    search: bool,
    page: str,
    query: dict[str, str | int] | None,
    expected: str,
) -> None:
    """Test URL generation."""
    result = url_of(
        user_id=user_id,
        venue_id=venue_id,
        brewery_id=brewery_id,
        beer_id=beer_id,
        search=search,
        page=page,
        query=query,
    )

    assert result == expected
    assert result.startswith(UNTAPPD_BASE_URL.rstrip("/"))
