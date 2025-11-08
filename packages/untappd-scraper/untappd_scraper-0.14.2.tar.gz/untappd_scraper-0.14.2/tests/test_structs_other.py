"""Test other helpers."""

from __future__ import annotations

from untappd_scraper.structs.other import Location


def test_location() -> None:
    loc1 = Location(lat=-33, lng=151)
    loc2 = Location(lat=-34, lng=151)

    result = loc1.distance_from(loc2)

    assert result > 0
