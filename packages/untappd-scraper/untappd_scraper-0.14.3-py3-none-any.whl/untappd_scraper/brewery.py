"""Untappd breweries."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any, Self

from dateutil.parser import parse as parse_date
from httpx import HTTPStatusError
from untappd_scraper.logging_config import configure_logging, logger
from untappd_scraper.web import (
    end_of_href,
    extract_checkin_elements_bs4,
    get_text,
    make_soup,
    parsed_value,
    url_of,
)
from utpd_models_web.brewery import WebBreweryDetails
from utpd_models_web.checkin import WebActivityBeer
from utpd_models_web.constants import UNTAPPD_BASE_URL

if TYPE_CHECKING:  # pragma: no cover
    from bs4 import BeautifulSoup


configure_logging(__name__)

logger.info("Loading brewery...")


@dataclass
class Brewery:
    """Untappd brewery."""

    brewery_id: int
    brewery_name: str = field(init=False)

    details: WebBreweryDetails = field(init=False, repr=False)
    activity: list[WebActivityBeer] = field(default_factory=list, init=False, repr=False)

    _soup: BeautifulSoup = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialise a Brewery object, storing the brewery ID and loading details.

        Raises:
            ValueError: invalid brewery ID
        """
        url = url_of(brewery_id=self.brewery_id)

        try:
            self._soup, _ = make_soup(url)
        except HTTPStatusError as e:
            logger.debug("Error getting brewery page for {}: {}", self.brewery_id, e)
            msg = f"Invalid brewery ID {self.brewery_id}"
            raise ValueError(msg) from e

        self.details = brewery_details(self._soup, brewery_id=self.brewery_id)
        self.brewery_name = self.details.name

        self.activity = brewery_activity(self._soup, brewery_id=self.brewery_id)

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Return unknown attributes from venue details.

        Args:
            name (str): attribute to lookup

        Returns:
            Any: attribute value
        """
        return getattr(self.details, name)

    @classmethod
    def from_name(cls, brewery_name: str) -> Self | None:
        """Search for a brewery name and return the first one returned.

        Args:
            brewery_name (str): brewery name to search

        Returns:
            brewery: populated brewery object with first match of brewery name
        """
        url = url_of(search=True, query={"q": brewery_name, "type": "brewery"})
        soup, _ = make_soup(url)

        beers_link = soup.select_one("div.details.brewery a")

        if not beers_link:
            logger.debug("No brewery found for %s", brewery_name)
            return None

        brewery_id = parsed_value("/{:d}/beer", str(beers_link["href"]))

        return cls(int(brewery_id)) if brewery_id else None

    @classmethod
    def from_url(cls, brewery_url: str) -> Self | None:
        """Navigate via a brewery url and return the brewery objecct.

        Args:
            brewery_url (str): brewery url to load

        Returns:
            brewery: populated brewery object for this brewery url
        """
        url = url_of(page=brewery_url)
        try:
            soup, _ = make_soup(url)
        except HTTPStatusError as e:
            logger.debug("Error getting brewery page for url {}: {}", brewery_url, e)
            return None

        rss = soup.select_one("p.rss a")
        href = str(rss["href"]) if rss else ""

        if not href:  # pragma: no cover
            logger.debug("No brewery found for url {}", brewery_url)
            return None

        brewery_id = href.split("/")[-1]

        return cls(int(brewery_id))


# ----- brewery processing -----


def brewery_details(soup: BeautifulSoup, *, brewery_id: int) -> WebBreweryDetails:
    """Parse a brewery's main page into brewery details.

    Args:
        soup (BeautifulSoup): brewery's main page parsed
        brewery_id (int): brewery ID

    Returns:
        WebBreweryDetails: general brewery details
    """
    name = get_text(soup, "div.name h1")
    style = get_text(soup, "div.name p.style")
    address = get_text(soup, "div.name p.brewery")

    # Remove the "Show Less" text
    if desc_el := soup.select_one("div.desc div.beer-descrption-read-less"):
        for a in desc_el.select("a.read-less"):
            a.decompose()  # Remove from the tree
        description = desc_el.get_text(strip=True)
    else:
        description = ""  # pragma: no cover

    beers = get_text(soup, "div.details p.count")
    beers_parsed = parsed_value("{:d} beers", beers)
    num_beers = int(beers_parsed) if beers_parsed is not None else 0

    rating_tag = soup.select_one("div.details div.caps")
    rating = float(rating_tag.get("data-rating", 0)) if rating_tag else None  # pyright: ignore[reportArgumentType]

    if canonical := soup.select_one('link[rel="canonical"]'):
        url = str(canonical["href"]).rstrip("/")
        brewery_url = url.removeprefix(UNTAPPD_BASE_URL)
    else:  # pragma: no cover
        brewery_url = f"brewery/{brewery_id}"

    return WebBreweryDetails(
        brewery_id=brewery_id,
        name=name,
        brewery_url=brewery_url,
        style=style,
        description=description,
        num_beers=num_beers,
        rating=rating,
        address=address,
    )


def brewery_activity(soup: BeautifulSoup, brewery_id: int) -> list[WebActivityBeer]:
    """Parse a brewery's activity page into checkins.

    Args:
        soup (BeautifulSoup): brewery's main page parsed
        brewery_id (int): brewery ID

    Returns:
        list[WebActivityBeer]: brewery activity
    """
    activity = []

    for beer in soup.select("div.activity div.item"):
        checkin_el = str(beer.get("data-checkin-id", ""))
        checkin_id = int(checkin_el) if checkin_el else 0
        time_el = beer.select_one(".time")
        checkin_time = parse_date(time_el.text) if time_el else datetime.min  # noqa: DTZ901
        label = img.get("src", "") if (img := soup.select_one("a.label img")) else ""

        user_el, beer_el, brewery_el, location_el = extract_checkin_elements_bs4(beer)
        purchased_el = beer.select_one("p.purchased a")

        if location_el and (location_href := end_of_href(location_el)):
            location_id = int(location_href)
        else:
            location_id = None
        if purchased_el and (purchased_href := end_of_href(purchased_el)):
            purchased_id = int(purchased_href)
        else:
            purchased_id = None

        purchased_at = str(purchased_el.text) if purchased_el else None

        rating_tag = soup.select_one("div.rating-serving div.caps")
        rating = float(rating_tag.get("data-rating", 0)) if rating_tag else None  # pyright: ignore[reportArgumentType]

        friends_tag = beer.select("div.tagged-friends a")
        friends = (
            [href for friend_tag in friends_tag if (href := end_of_href(friend_tag))]
            if friends_tag
            else None
        )

        brewery_url = (brewery_el.a and brewery_el.a.get("href")) or brewery_el.get("href")
        brewery_url = str(brewery_url).removesuffix("/") if brewery_url else ""

        activity.append(
            WebActivityBeer(
                checkin_id=checkin_id,
                checkin=checkin_time,
                user_name=end_of_href(user_el) or "",
                beer_name=beer_el.text,
                beer_label_url=str(label),
                beer_id=int(end_of_href(beer_el) or 0),
                brewery_name=brewery_el.text,
                brewery_id=brewery_id,
                brewery_url=brewery_url,
                location=location_el.text if location_el else None,
                location_id=location_id,
                purchased_at=purchased_at,
                purchased_id=purchased_id,
                comment=get_text(beer, "p.comment-text"),
                serving=get_text(beer, "p.serving"),
                user_rating=rating,
                friends=friends,
            )
        )

    return activity
