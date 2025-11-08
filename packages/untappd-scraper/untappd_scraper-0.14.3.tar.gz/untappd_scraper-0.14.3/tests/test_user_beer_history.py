"""Test user beer history."""

from __future__ import annotations

from bs4 import BeautifulSoup

from untappd_scraper.user_beer_history import calc_beers_per_brewery
from untappd_scraper.web import end_of_href

# ----- Tests -----


def test_calc_beers_per_brewery() -> None:
    html = """
        <label>Filter by Brewery</label>
            <div>
                <p>
                    <span class="selected-text">All</span>
                </p>
                <select id="brewery_picker" aria-label="Brewery picker">
                    <option value="all">All</option>
                    <option value="3436">10 Barrel Brewing Co. (1)</option>
                    <option value="253657">10 Toes Brewery (2)</option>
                    <option value="3557">2 Brothers Brewery (5)</option>
                    <option value="484738">Bucketty's Brewing Co. (84)</option>
                </select>
            </div>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = calc_beers_per_brewery(soup)

    assert result == {3436: 1, 253657: 2, 3557: 5, 484738: 84}


def test_id_from_href2() -> None:
    html = """
    <a class="track-click" data-track="distinctbeers" data-href=":firstCheckin" 
        href="/user/mw1414/checkin/1125035430/"><abbr class="">01/30/22</abbr></a>
        """

    soup = BeautifulSoup(html, "html.parser")

    result = end_of_href(soup)

    assert result == "1125035430"


def test_id_from_href2_invalid() -> None:
    html = """
    <a href="nowhere" class="beer-name">Beer Name</a>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = end_of_href(soup)

    assert result is None


def test_id_from_href2_missing() -> None:
    html = """
    <a data-href="/beer/1234567" class="beer-name">Beer Name</a>
    """
    soup = BeautifulSoup(html, "html.parser")

    result = end_of_href(soup)

    assert result is None
