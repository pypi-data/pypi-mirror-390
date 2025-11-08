"""Untappd venues."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import parse
from httpx import URL
from untappd_scraper.beer import checkin_activity
from untappd_scraper.html_session import get
from untappd_scraper.venue_menus import venue_menus
from untappd_scraper.web import id_from_href, url_of
from utpd_models_web.constants import UNTAPPD_BASE_URL
from utpd_models_web.other import Location
from utpd_models_web.venue import WebVenueDetails

if TYPE_CHECKING:  # pragma: no cover
    from requests_html import HTMLResponse
    from utpd_models_web.checkin import WebActivityBeer
    from utpd_models_web.menu import WebVenueMenu

logger = logging.getLogger(__name__)


@dataclass
class Venue:
    """Untappd venue."""

    venue_id: int
    venue_name: str = field(init=False)

    _page: HTMLResponse = field(init=False, repr=False)
    _venue_details: WebVenueDetails = field(init=False, repr=False)
    activity_details: list[WebActivityBeer] = field(
        default_factory=list, init=False, repr=False
    )
    _menu_details: set[WebVenueMenu] = field(default_factory=set, init=False, repr=False)

    def __post_init__(self) -> None:
        """Initiate a Venue object, storing the venue ID and loading details.

        Raises:
            ValueError: invalid venue ID
        """
        self._page = get(url_of(venue_id=self.venue_id))  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]
        if not self._page.ok:
            msg = f"Invalid venue ID {self.venue_id} ({self._page})"
            raise ValueError(msg)

        self._venue_details = venue_details(resp=self._page)
        self.venue_name = self._venue_details.name

        self.activity_details = []
        self._menu_details = set()

    def menus(self, menu_name: str | None = None) -> set[WebVenueMenu]:
        """Scrape venue main page (if not done already) and return any menus.

        Args:
            menu_name (str): Only return menus with names matching this

        Returns:
            set[WebVenueMenu]: all menus found for venue. Empty if unverified
        """
        if not self._venue_details.is_verified:
            return set()

        if not self._menu_details:
            self._menu_details = venue_menus(self._page)

        if menu_name:
            return {
                menu
                for menu in self._menu_details
                if menu_name.casefold() in menu.name.casefold()
            }
        return self._menu_details

    def activity(self) -> list[WebActivityBeer]:
        """Return a venue's recent checkins.

        Returns:
            list[WebActivityBeer]: last 25 (or so) checkins
        """
        if not self.activity_details:
            resp = get(self._venue_details.activity_url)  # pyright: ignore[reportArgumentType]
            self.activity_details = list(dict.fromkeys(checkin_activity(resp)))  # pyright: ignore[reportArgumentType]

        return self.activity_details

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Return unknown attributes from venue details.

        Args:
            name (str): attribute to lookup

        Returns:
            Any: attribute value
        """
        return getattr(self._venue_details, name)

    @classmethod
    def from_name(cls, venue_name: str) -> Venue | None:  # pragma: no cover
        """Search for a venue name and return the first one returned.

        Args:
            venue_name (str): venue name to search

        Returns:
            Venue: populated Venue object with first match of venue name
        """
        resp = get(
            f"{UNTAPPD_BASE_URL}search",
            params={"q": venue_name, "type": "venues", "sort": "popular_recent"},  # pyright: ignore[reportCallIssue]
        )
        if not resp.ok:
            return None
        first_match = resp.html.find(".beer-item .label", first=True)
        venue_id = id_from_href(first_match)
        logger.debug("Looking up name %s returned ID %d", venue_name, venue_id)
        return cls(venue_id)


# ----- venue processing -----


def venue_details(resp: HTMLResponse) -> WebVenueDetails:
    """Parse a venue's main page into venue details.

    Args:
        resp (HTMLResponse): venue's main page loaded

    Returns:
        WebVenueDetails: general venue details
    """
    venue_page = resp.html.find(".venue-page", first=True)
    venue_header = venue_page.find(".venue-header", first=True)  # pyright: ignore[reportAttributeAccessIssue]

    verified = bool(venue_page.find(".menu-header", first=True))  # pyright: ignore[reportAttributeAccessIssue]
    venue_id = int(venue_page.attrs["data-venue-id"])  # pyright: ignore[reportAttributeAccessIssue]
    venue_slug = venue_page.attrs["data-venue-slug"]  # pyright: ignore[reportAttributeAccessIssue]

    name_el = venue_header.find(".venue-name", first=True)  # pyright: ignore[reportAttributeAccessIssue]
    name = name_el.find("h1", first=True).text  # pyright: ignore[reportAttributeAccessIssue]
    categories = set(name_el.find("h2", first=True).text.split(", "))  # pyright: ignore[reportAttributeAccessIssue]

    try:
        address: str = name_el.find("p.address", first=True).text  # pyright: ignore[reportAttributeAccessIssue]
    except AttributeError:  # pragma: no cover
        address = ""
    else:
        address = address.removesuffix("( Map )").strip()

    if map_link := name_el.find("a", first=True):  # pyright: ignore[reportAttributeAccessIssue]
        link_href = map_link.attrs["href"]  # pyright: ignore[reportAttributeAccessIssue]
        loc_match = parse.search("near={:f},{:f}", link_href) or parse.search(
            "q={:f},{:f}", link_href
        )
        location: Location | None = Location(*loc_match) if loc_match else None  # pyright: ignore[reportGeneralTypeIssues]
    else:  # pragma: no cover
        location = None

    # proxying via utpd-http2 doesn't update the URL for redirects
    url = URL(resp.url).join(f"/v/{venue_slug}/{venue_id}")

    return WebVenueDetails(
        venue_id=venue_id,
        name=name,
        is_verified=verified,
        venue_slug=venue_slug,
        categories=categories,
        address=address,
        location=location,
        url=str(url),
    )
