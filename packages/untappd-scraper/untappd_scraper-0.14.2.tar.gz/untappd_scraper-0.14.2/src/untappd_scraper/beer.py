"""Untappd beers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from dateutil.parser import parse as parse_date
from requests_html import Element
from utpd_models_web.beer import WebBeerDetails
from utpd_models_web.checkin import WebActivityBeer
from utpd_models_web.constants import UNTAPPD_BASE_URL

from untappd_scraper.html_session import get
from untappd_scraper.logging_config import logger
from untappd_scraper.web import id_from_href, parse_abv, parsed_value, slug_from_href

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterator

    from requests_html import HTMLResponse


@dataclass
class Beer:
    """Untappd beer."""

    beer_id: int
    beer_name: str = field(init=False)

    _page: HTMLResponse = field(init=False, repr=False)
    _beer_details: WebBeerDetails = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Post-init method to load beer details."""
        self._page = get(url_of(self.beer_id))  # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]
        if not self._page.ok:
            msg = f"Invalid beer ID {self.beer_id} ({self._page})"
            raise ValueError(msg)

        self._beer_details = beer_details(resp=self._page)
        self.beer_name = self._beer_details.beer_name

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Return unknown attributes from beer details.

        Args:
            name (str): attribute to lookup

        Returns:
            Any: attribute value
        """
        return getattr(self._beer_details, name)


# ----- utils -----


def url_of(beer_id: int) -> str:
    """Return the URL for a beer's main page.

    Args:
        beer_id (int): beer ID

    Returns:
        str: url to load to get beer's main page
    """
    return f"{UNTAPPD_BASE_URL}beer/{beer_id}"


# ----- beer details processing -----


def beer_details(resp: HTMLResponse) -> WebBeerDetails:
    """Parse a user's main page into user details.

    Args:
        resp (HTMLResponse): beer's main page loaded

    Returns:
        WebBeerDetails: general beer details
    """
    content_el = resp.html.find(".main .content", first=True)
    description = "".join(  # pyright: ignore[reportCallIssue]
        content_el.find(".desc .beer-descrption-read-less", first=True).xpath("//div/text()")  # pyright: ignore[reportAttributeAccessIssue, reportArgumentType]
    ).strip()

    return WebBeerDetails(
        beer_id=id_from_href(content_el.find("a.check", first=True)),  # pyright: ignore[reportAttributeAccessIssue, reportArgumentType]
        beer_name=content_el.find(".name h1", first=True).text,  # pyright: ignore[reportAttributeAccessIssue]
        beer_description=description.strip(),
        beer_label_url=content_el.find(".label img", first=True).attrs["src"],  # pyright: ignore[reportAttributeAccessIssue]
        brewery_name=content_el.find(".name .brewery a", first=True).text,  # pyright: ignore[reportAttributeAccessIssue]
        brewery_url=(content_el.find(".name .brewery a", first=True))  # pyright: ignore[reportAttributeAccessIssue]
        .attrs["href"]  # pyright: ignore[reportAttributeAccessIssue]
        .removesuffix("/"),
        style=content_el.find(".name p.style", first=True).text,  # pyright: ignore[reportAttributeAccessIssue]
        abv=parse_abv(content_el.find(".details p.abv", first=True).text),  # pyright: ignore[reportAttributeAccessIssue]
        url=resp.url,
        global_rating=content_el.find(".details [data-rating]", first=True).attrs[  # pyright: ignore[reportAttributeAccessIssue]
            "data-rating"
        ],
        num_ratings=parsed_value(  # pyright: ignore[reportArgumentType]
            "{:d} Rat",
            content_el.find(".details p.raters", first=True).text,  # pyright: ignore[reportAttributeAccessIssue]
        ),
    )


def checkin_activity(resp: HTMLResponse) -> Iterator[WebActivityBeer]:
    """Parse all available recent checkins for a user or in a venue.

    Args:
        resp (HTMLResponse): user's main page or venue's activity page

    Returns:
        Iterator[WebActivityBeer]: user's visible recent checkins
    """
    return (checkin_details(checkin) for checkin in resp.html.find(".activity .item"))  # pyright: ignore[reportGeneralTypeIssues]


def checkin_details(checkin_item: Element) -> WebActivityBeer:
    """Extract beer details from a checkin.

    Args:
        checkin_item (Element): single checkin

    Returns:
        WebActivityBeer: Interesting details for a beer
    """
    user_el, beer_el, brewery_el, location_el = extract_checkin_elements(checkin_item)

    checkin_time_el = checkin_item.find(".bottom .time", first=True)
    checkin_time = checkin_time_el.attrs.get("data-gregtime", checkin_time_el.text)  # pyright: ignore[reportAttributeAccessIssue]
    checkin_time = parse_date(checkin_time)
    assert checkin_time.tzinfo
    assert checkin_time.tzinfo.utcoffset(checkin_time) is not None, (
        f"Naive datetime from {checkin_time_el.html=}"  # pyright: ignore[reportAttributeAccessIssue]
    )

    if (img := checkin_item.find("a.label img", first=True)) and isinstance(img, Element):
        label = img.attrs["src"]
    else:
        label = ""  # pragma: no cover

    purchased_at = checkin_item.find(".purchased a", first=True)
    try:
        comment = checkin_item.find("p.comment-text", first=True).text  # pyright: ignore[reportAttributeAccessIssue]
    except AttributeError:
        comment = None
    serving = checkin_item.find(".serving", first=True)

    data_rating_element = checkin_item.find("[data-rating]", first=True)
    if data_rating_element:
        data_rating: float | None = float(data_rating_element.attrs["data-rating"])  # pyright: ignore[reportAttributeAccessIssue]
    else:
        data_rating = None  # pragma: no cover

    try:
        friends: list[str] | None = [
            slug_from_href(href)
            for href in checkin_item.find(".tagged-friends a")  # pyright: ignore[reportGeneralTypeIssues]
        ]
    except AttributeError:  # pragma: no cover
        friends = None

    if brewery_link := brewery_el.find("a", first=True):
        brewery_url: str = brewery_link.attrs["href"].strip("/")  # pyright: ignore[reportAttributeAccessIssue]

        last_bit = brewery_url.rsplit("/", 1)[-1]
        brewery_id = int(last_bit) if last_bit.isdigit() else None
    else:
        logger.error("No brewery link found in %s", brewery_el.html)
        msg = f"No brewery link found for beer {beer_el.text}"
        raise ValueError(msg)  # pragma: no cover

    try:
        beer_id = id_from_href(beer_el)
    except ValueError:
        logger.exception("Failed to parse beer ID from %s", beer_el.html)
        beer_id = 0

    return WebActivityBeer(
        checkin_id=int(checkin_item.attrs["data-checkin-id"]),
        checkin=checkin_time,
        user_name=slug_from_href(user_el),
        beer_id=beer_id,
        beer_label_url=label,
        beer_name=beer_el.text,
        brewery_name=brewery_el.text,
        brewery_id=brewery_id,
        brewery_url=brewery_url,
        location=location_el.text if location_el else None,
        location_id=id_from_href(location_el) if location_el else None,
        purchased_at=purchased_at.text if purchased_at else None,  # pyright: ignore[reportAttributeAccessIssue]
        purchased_id=id_from_href(purchased_at) if purchased_at else None,  # pyright: ignore[reportArgumentType]
        comment=comment,
        serving=serving.text if serving else None,  # pyright: ignore[reportAttributeAccessIssue]
        user_rating=data_rating,
        friends=friends,
    )


def extract_checkin_elements(
    element: Element,
) -> tuple[Element, Element, Element, Element | None]:
    """Extract four linked elements in a checkin.

    Args:
        element (Element): checkin element

    Raises:
        ValueError: element passed didn't contain 3-4 <a> tags

    Returns:
        tuple[Element, Element, Element, Element]: user, beer, brewery, location
    """
    elements = element.find(".top .text a")

    if len(elements) == 3:  # noqa: PLR2004  # pyright: ignore[reportArgumentType]
        return [*elements, None]  # pyright: ignore[reportGeneralTypeIssues, reportReturnType]
    if len(elements) == 4:  # noqa: PLR2004  # pyright: ignore[reportArgumentType]
        return elements  # pyright: ignore[reportReturnType]

    msg = f"Wanted 3 or 4 <a> elements (not {len(elements)}) in {element.html}"  # pyright: ignore[reportArgumentType]
    raise ValueError(msg)
