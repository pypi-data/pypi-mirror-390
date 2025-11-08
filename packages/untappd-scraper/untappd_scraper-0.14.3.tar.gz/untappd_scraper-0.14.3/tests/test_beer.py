"""Test beer scraping."""

from __future__ import annotations

from datetime import datetime
from string import Template
from typing import Final
from zoneinfo import ZoneInfo

import pytest
from bs4 import BeautifulSoup
from requests_html import HTML
from untappd_scraper.beer import Beer, extract_checkin_elements
from untappd_scraper.web import extract_checkin_elements_bs4, url_of
from utpd_models_web.checkin import WebActivityBeer
from utpd_models_web.constants import UNTAPPD_BASE_URL


@pytest.fixture
def beer(_mock_beer_get: None) -> Beer:
    return Beer(123)


# ----- Tests -----


def test_url_of() -> None:
    result = url_of(beer_id=12345)

    assert result == f"{UNTAPPD_BASE_URL}beer/12345"


def test_beer(beer: Beer) -> None:
    result = beer

    assert result
    assert result.beer_name
    assert result.beer_name == result.beer_name
    assert result.brewery_name
    assert result.beer_id
    assert result.brewery_url


@pytest.mark.usefixtures("_mock_beer_404")
def test_beer_invalid() -> None:
    with pytest.raises(ValueError, match="Invalid"):
        Beer(123)


class TestExtractCheckinElements:
    """Test the extraction of checkin elements."""

    by: Final = 'by <a href="/MountainCulture">Mountain Culture Beer Co.</a>'
    at: Final = 'at <a href="/v/the-taproom/12500353">The Taproom</a>'

    html_base: Final = Template(
        """
        <div class="activity box">
        <div class="content">
        <h3>$user_name's Recent Activity</h3>
        <div id="main_stream">
        
        <div class="item">
        <div class="checkin">
            <div class="top">
            <p class="text">
                <a href="/user/$user_slug" class="user">$user_name</a>
                is drinking a <a href="/b/$beer_slug/$beer_id">$beer_name</a>
                $by
                $at
            </p>
            </div>
        </div>
        </div>
        
        </div>
        </div>
        </div>
    """
    ).substitute(
        user_slug="mw1414",
        user_name="Wardy",
        beer_slug="mountain-culture-beer-co-cult-ipa",
        beer_id=3484719,
        beer_name="Cult IPA",
        # sub'd later
        by="$by",
        at="$at",
    )
    html: Final = Template(html_base)

    def test_all(self) -> None:  # sourcery skip: class-extract-method
        """Test that the checkin elements are extracted correctly."""
        # fully populated
        html = self.html.substitute(by=self.by, at=self.at)
        doc = HTML(html=html)
        el = doc.find(".activity .item", first=True)

        result = extract_checkin_elements(el)  # pyright: ignore[reportArgumentType]

        assert all(r is not None for r in result)

    def test_no_at(self) -> None:
        """Test that the checkin elements are extracted correctly."""
        # no location
        html = self.html.substitute(by=self.by, at="")
        doc = HTML(html=html)
        el = doc.find(".activity .item", first=True)

        result = extract_checkin_elements(el)  # pyright: ignore[reportArgumentType]

        assert all(r is not None for r in result[:-1])
        assert result[-1] is None

    def test_no_by(self) -> None:
        # invalid
        html = self.html.substitute(by="", at="")
        doc = HTML(html=html)
        el = doc.find(".activity .item", first=True)

        with pytest.raises(ValueError, match="Wanted"):
            extract_checkin_elements(el)  # pyright: ignore[reportArgumentType]

    def test_all_bs4(self) -> None:  # sourcery skip: class-extract-method
        """Test that the checkin elements are extracted correctly."""
        # fully populated
        html = self.html.substitute(by=self.by, at=self.at)
        soup = BeautifulSoup(html, "html.parser")
        el = soup.select_one(".activity .item")
        assert el

        result = extract_checkin_elements_bs4(el)

        assert all(r is not None for r in result)

    def test_no_at_bs4(self) -> None:
        """Test that the checkin elements are extracted correctly."""
        # no location
        html = self.html.substitute(by=self.by, at="")
        soup = BeautifulSoup(html, "html.parser")
        el = soup.select_one(".activity .item")
        assert el

        result = extract_checkin_elements_bs4(el)

        assert all(r is not None for r in result[:-1])
        assert result[-1] is None

    def test_no_by_bs4(self) -> None:
        # invalid
        html = self.html.substitute(by="", at="")
        soup = BeautifulSoup(html, "html.parser")
        el = soup.select_one(".activity .item")
        assert el

        with pytest.raises(ValueError, match="Wanted"):
            extract_checkin_elements_bs4(el)


def test_web_activity_beer_str() -> None:
    beer = WebActivityBeer(
        checkin_id=123,
        checkin=datetime(2025, 4, 13, 9, 32, tzinfo=ZoneInfo("Australia/Sydney")),
        user_name="Wardy",
        beer_name="Cult IPA",
        beer_id=3484719,
        brewery_name="Mountain Culture Beer Co.",
        brewery_id=446724,
        brewery_url="mountain-culture-beer-co",
        location="The Taproom",
        serving="Draft",
        user_rating=4.2,
        friends=["Shoey", "Pete"],
        beer_label_url="label_url",
    )

    result = str(beer)

    assert (
        result == "Sun 09:32: Wardy - Cult IPA by Mountain Culture Beer Co. "
        "at The Taproom (Draft), "
        "user rating 4.2 with Shoey, Pete"
    )


def test_web_beer_details_str_minimal() -> None:
    beer = WebActivityBeer(
        checkin_id=123,
        checkin=datetime(2025, 4, 13, 9, 32, tzinfo=ZoneInfo("Australia/Sydney")),
        user_name="Wardy",
        beer_name="Cult IPA",
        beer_id=3484719,
        brewery_name="Mountain Culture Beer Co.",
        brewery_id=446724,
        brewery_url="mountain-culture-beer-co",
        beer_label_url="label_url",
    )

    result = str(beer)

    assert result == "Sun 09:32: Wardy - Cult IPA by Mountain Culture Beer Co."


# ----- Tests whilst cutting over to ut-types -----


def test_web_beer_details() -> None:
    beer = Beer(3706439)

    result = beer.beer_name

    assert result == "Annabelle's XPA"


def test_web_beer_eq() -> None:
    beer1 = Beer(5892921)._beer_details
    beer2 = Beer(5892921)._beer_details

    assert beer1 == beer2
    assert beer1 is not beer2


def test_web_beer_le() -> None:
    beer1 = Beer(3706439)._beer_details
    beer2 = Beer(6197112)._beer_details

    result = beer1 <= beer2

    assert result
