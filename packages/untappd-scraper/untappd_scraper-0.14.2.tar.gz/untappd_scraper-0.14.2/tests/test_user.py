"""Test user scraping."""

from __future__ import annotations

import pytest
from untappd_scraper.user import User
from untappd_scraper.user_lists import WebUserList
from utpd_models_web.constants import UNTAPPD_BEER_HISTORY_SIZE
from utpd_models_web.user import WebUserDetails

# ----- Tests -----


@pytest.mark.webtest
def test_user() -> None:
    result = User("mw1414")  # Wardy

    assert result
    assert result.name
    assert result.user_id
    assert result.user_name


@pytest.mark.webtest
def test_user_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid"):
        User("wardysliver")


@pytest.mark.webtest
def test_user_mw1414() -> None:
    result = User("mw1414")

    assert result
    assert isinstance(result.details, WebUserDetails)
    assert isinstance(result.activity, tuple)
    assert result.activity
    assert result.user_name == "Wardy"


@pytest.mark.webtest
def test_activity_mw1414() -> None:
    user = User("mw1414")

    result = user.activity

    assert result
    assert isinstance(result, tuple)
    assert any(r.checkin_id for r in result)
    assert any(r.beer_id for r in result)
    assert any(r.serving == "Draft" for r in result)  # Wardy has a draft beer checkin, surely
    assert all("jpeg" in r.beer_label_url or "png" in r.beer_label_url for r in result)
    assert all(r.brewery_url and "tba" not in r.brewery_url.casefold() for r in result)


@pytest.fixture(scope="module")
def wardy_user() -> User:
    """Create a real, web-scraped user."""
    return User("mw1414")


@pytest.mark.webtest
def test_beer_history(wardy_user: User) -> None:
    result = wardy_user.beer_history()

    assert result
    assert len(result.results) == UNTAPPD_BEER_HISTORY_SIZE
    assert len({b.beer_id for b in result.results}) == UNTAPPD_BEER_HISTORY_SIZE
    assert result.results[0].beer_name
    assert result.results[0].brewery_name
    assert result.results[0].recent_checkin_id
    assert not result.found_all  # way more than one page of uniques
    assert "total_found=25," in repr(result)
    assert all("assets" in r.beer_label_url for r in result.results)
    assert all(r.brewery_url and r.brewery_url != "TBA" for r in result.results)
    assert all(r.beer_label_url for r in result.results)


@pytest.mark.webtest
def test_beer_brewery_history_alesmith(wardy_user: User) -> None:
    # As of Apr 2025, Wardy had 31 Alesmith beers
    result = wardy_user.brewery_history(brewery_id=2471, max_resorts=1)

    assert result
    assert result.total_found
    assert result.found_all
    assert all(r.beer_label_url for r in result.results)


@pytest.mark.webtest
def test_beer_brewery_history_buckettys(wardy_user: User) -> None:
    # As of May 2025, Wardy had 86 bucketty's beers
    # and an English IPA was elusive in re-sorts
    result = wardy_user.brewery_history(brewery_id=484738, max_resorts=99)

    assert result
    assert len(result.results) > UNTAPPD_BEER_HISTORY_SIZE
    assert len(result.results) >= 86
    assert result.found_all
    assert all(r.beer_label_url for r in result.results)


# NOTE this is huge. Probably should skip of limit resorts
@pytest.mark.webtest
def test_beer_brewery_history_4pines(wardy_user: User) -> None:
    max_resorts = 3
    # As of Apr 2025, Wardy had 569 4 Pines beers!!
    result = wardy_user.brewery_history(brewery_id=4254, max_resorts=max_resorts)

    assert result
    assert result.total_expected >= 569
    # expect more than just the pages we requested, as style sort will grab more
    assert result.total_found > UNTAPPD_BEER_HISTORY_SIZE * max_resorts
    assert not result.found_all
    assert all(r.beer_label_url for r in result.results)


@pytest.mark.webtest
def test_lists() -> None:
    user = User("mw1414")
    lists = user.lists()
    assert len(lists) == 13

    result = lists[1]  # 0 is wish list

    assert result.description
    assert result.num_items


@pytest.mark.webtest
def test_lists_detail() -> None:
    user = User("mw1414")
    lists = user.lists()
    fridge = lists[1]  # should be fridge
    lists = user.lists_detail(fridge.name)
    assert len(lists) == 1

    result = lists[0]

    assert isinstance(result, WebUserList)
    assert len(result.beers) == result.num_items
    assert result.full_scrape


@pytest.mark.webtest
def test_venue_history() -> None:
    user = User("mw1414")
    history = user.venue_history()
    assert len(history) == UNTAPPD_BEER_HISTORY_SIZE

    result = next(iter(history))

    assert result.venue_id
    assert result.first_checkin_id
    assert result.last_checkin_id
