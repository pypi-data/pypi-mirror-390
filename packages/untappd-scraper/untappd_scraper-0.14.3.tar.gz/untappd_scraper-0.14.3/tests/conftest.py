"""Common fixtures for tests."""

from __future__ import annotations

from functools import partial
from pathlib import Path

import pytest
from requests_html import HTML
from untappd_scraper.html_session import get
from utpd_models_web.constants import UNTAPPD_BASE_URL

# ----- Pre-loaded HTML responses -----


@pytest.fixture
def beer_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}beer/123456", html=Path("tests/html/beer.html").read_text()
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def fridge_list_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}user/test/lists/201107",
        html=Path("tests/html/fridge-list.html").read_text(),
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def user_venue_history_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}user/test/venues?sort=recent",
        html=Path("tests/html/user-venue-history.html").read_text(),
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def user_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}user/test", html=Path("tests/html/user.html").read_text()
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def user_lists_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}user/test/lists",
        html=Path("tests/html/userlists.html").read_text(),
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def venue_unv_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}venue/14705",
        html=Path("tests/html/venue_unv.html").read_text(),
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def venue_ver_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}venue/107565",
        html=Path("tests/html/venue_ver.html").read_text(),
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def venue_ver_activity_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}venue/107565/activity",
        html=Path("tests/html/venue_ver_activity.html").read_text(),
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def venue_ver_nest_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}venue/5840988",
        html=Path("tests/html/venue_ver_nest.html").read_text(),
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def wishlist_html() -> HTML:
    return HTML(
        url=f"{UNTAPPD_BASE_URL}user/test/wishlist",
        html=Path("tests/html/wishlist.html").read_text(),
    )  # pyright: ignore[reportArgumentType]


@pytest.fixture
def list_page_1_html() -> HTML:
    return HTML(html=Path("tests/html/user-list-1.html").read_text())  # pyright: ignore[reportArgumentType]


@pytest.fixture
def list_page_2_html() -> HTML:
    return HTML(html=Path("tests/html/user-list-2.html").read_text())  # pyright: ignore[reportArgumentType]


# ----- Wrap HTML responses to provide, eg, .html attribute -----


class MockResponse:
    """Mock response object for requests_html.HTML."""

    def __init__(self, html: HTML) -> None:
        """Initialize with given HTML."""
        self.html = html
        self.ok = True
        self.url = html.url


@pytest.fixture
def beer_resp(beer_html: HTML) -> MockResponse:
    return MockResponse(beer_html)


@pytest.fixture
def user_resp(user_html: HTML) -> MockResponse:
    return MockResponse(user_html)


@pytest.fixture
def fridge_list_resp(fridge_list_html: HTML) -> MockResponse:
    return MockResponse(fridge_list_html)


@pytest.fixture
def user_venue_history_resp(user_venue_history_html: HTML) -> MockResponse:
    return MockResponse(user_venue_history_html)


@pytest.fixture
def user_lists_resp(user_lists_html: HTML) -> MockResponse:
    return MockResponse(user_lists_html)


@pytest.fixture
def venue_unv_resp(venue_unv_html: HTML) -> MockResponse:
    return MockResponse(venue_unv_html)


@pytest.fixture
def venue_ver_resp(venue_ver_html: HTML) -> MockResponse:
    return MockResponse(venue_ver_html)


@pytest.fixture
def venue_ver_nest_resp(venue_ver_nest_html: HTML) -> MockResponse:
    return MockResponse(venue_ver_nest_html)


@pytest.fixture
def list_page_1_resp(list_page_1_html: HTML) -> MockResponse:
    return MockResponse(list_page_1_html)


@pytest.fixture
def list_page_2_resp(list_page_2_html: HTML) -> MockResponse:
    return MockResponse(list_page_2_html)


# ----- Monkey patchers -----


@pytest.fixture
def _mock_beer_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("untappd_scraper.beer.get", partial(get, emulate_404=True))  # pyright: ignore[reportCallIssue]


@pytest.fixture
def _mock_beer_get(beer_resp: MockResponse, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("untappd_scraper.beer.get", lambda _: beer_resp)


@pytest.fixture
def _mock_user_get(user_resp: MockResponse, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("untappd_scraper.user.get", lambda _: user_resp)


@pytest.fixture
def _mock_user_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("untappd_scraper.user.get", partial(get, emulate_404=True))  # pyright: ignore[reportCallIssue]


@pytest.fixture
def _mock_user_venue_history_get(
    user_venue_history_resp: MockResponse, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "untappd_scraper.user_venue_history.get", lambda _: user_venue_history_resp
    )


@pytest.fixture
def _mock_user_lists_get(
    user_lists_resp: MockResponse, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("untappd_scraper.user_lists.get", lambda _: user_lists_resp)


@pytest.fixture
def _mock_venue_unv_get(venue_unv_resp: MockResponse, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("untappd_scraper.venue.get", lambda _: venue_unv_resp)


@pytest.fixture
def _mock_venue_ver_get(venue_ver_resp: MockResponse, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("untappd_scraper.venue.get", lambda _: venue_ver_resp)


@pytest.fixture
def _mock_venue_ver_nest_get(
    venue_ver_nest_resp: MockResponse, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("untappd_scraper.venue.get", lambda _: venue_ver_nest_resp)


@pytest.fixture
def _mock_venue_404(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("untappd_scraper.venue.get", partial(get, emulate_404=True))  # pyright: ignore[reportCallIssue]
