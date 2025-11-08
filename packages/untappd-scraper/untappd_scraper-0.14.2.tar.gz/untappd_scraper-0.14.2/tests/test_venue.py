"""Test venue scraping."""

from __future__ import annotations

import pytest
from untappd_scraper.venue import Venue
from utpd_models_web.constants import UNTAPPD_VENUE_ACTIVITY_SIZE


@pytest.fixture
def venue_unv(_mock_venue_unv_get: None) -> Venue:
    """Eg, 4 Pines is unverified."""
    return Venue(14705)


@pytest.fixture
def venue_ver(_mock_venue_ver_get: None) -> Venue:
    """Eg, Sweeneys is verified with multuple menus."""
    return Venue(107565)


@pytest.fixture
def venue_nest(_mock_venue_ver_nest_get: None) -> Venue:
    """Eg, Dad & Daves have a menu pulldown."""
    return Venue(5840988)


# ----- Tests -----


def test_venue(venue_unv: Venue) -> None:
    result = venue_unv

    assert result
    assert result.name
    assert result.venue_id
    assert result.categories
    assert result.venue_name


@pytest.mark.usefixtures("_mock_venue_404")
def test_user_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid"):
        Venue(123)  # ignored


def test_menus_unverified(venue_unv: Venue) -> None:
    result = venue_unv.menus()

    assert not result


@pytest.fixture
def venue(request: pytest.FixtureRequest) -> Venue:
    return request.getfixturevalue(request.param)


@pytest.mark.parametrize("venue", ["venue_ver", "venue_nest"], indirect=True)
def test_menus_verified(venue: Venue) -> None:
    menus = venue.menus()
    assert len(menus) >= 4

    result = next(iter(menus))

    assert result.beers
    assert result.full_name
    assert all("untappd" in r.beer_label_url for r in result.beers)
    assert all(r.brewery_id for r in result.beers)
    assert not any(r.brewery_url for r in result.beers)


def test_menus_named_verified(venue_ver: Venue) -> None:
    menus = venue_ver.menus("rooftop")
    assert len(menus) == 1

    result = next(iter(menus))

    assert result.name.casefold() == "rooftop"
    assert result.menu_id


@pytest.mark.xfail(reason="i think i need to patch /activity page")
def test_activity_verified(venue_ver: Venue) -> None:
    history = venue_ver.activity()
    assert history
    assert len(history) == UNTAPPD_VENUE_ACTIVITY_SIZE

    result = history[0]

    assert result.beer_id
    assert result.location
    assert result.beer_label_url
    assert result.brewery_url


def test_activity_unverified(venue_unv: Venue) -> None:
    history = venue_unv.activity()
    assert history
    assert len(history) == UNTAPPD_VENUE_ACTIVITY_SIZE

    result = history[0]

    assert result.beer_id
    assert result.location
    assert result.beer_label_url
    assert result.brewery_url


@pytest.mark.webtest
def test_activity_verified_live() -> None:
    venue = Venue(107565)  # Sweeneys

    result = venue.activity()

    assert result
    assert any(r.beer_name for r in result)


@pytest.mark.webtest
def test_activity_unverified_live() -> None:
    venue = Venue(14705)  # 4 Pines

    result = venue.activity()

    assert result
    assert any(r.beer_name for r in result)


@pytest.mark.webtest
def test_menu_brewery_id() -> None:
    venue = Venue.from_name("sweeneys")
    assert venue
    menu = next(iter(venue.menus()))

    result = menu.beers

    assert result
    assert all(b.brewery_id for b in result)


@pytest.mark.webtest
def test_menu_verified() -> None:
    venue = Venue(5840988)  # Dad & Daves

    result = venue.menus()

    assert result
    assert len({r.name for r in result}) >= 4

    menu = next((r for r in result if r.beers), None)  # pick a beer menu

    assert menu
    assert menu.beers
    assert all(b.brewery_id for b in menu.beers)
    assert not any(b.brewery_url for b in menu.beers)


@pytest.mark.webtest
def test_checkin_brewery_slug() -> None:
    venue = Venue.from_name("sweeneys")
    assert venue

    result = venue.activity()

    assert result
    assert all(b.brewery_url for b in result)
