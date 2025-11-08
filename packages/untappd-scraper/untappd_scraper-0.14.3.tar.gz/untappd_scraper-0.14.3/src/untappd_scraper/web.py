"""Utilities to process web data."""

from __future__ import annotations

from typing import TYPE_CHECKING

import parse
from bs4 import BeautifulSoup, Tag
from dateutil.parser import parse as parse_date
from httpx import URL
from utpd_models_web.constants import UNTAPPD_BASE_URL

from untappd_scraper.client import client
from untappd_scraper.logging_config import logger

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Mapping
    from datetime import datetime

    from requests_html import Element

logger.info("Loading web...")


def url_of(  # noqa: PLR0913
    user_id: str = "",
    *,
    venue_id: str = "",
    brewery_id: str | int = "",
    beer_id: str | int = "",
    search: bool = False,
    page: str = "",
    query: Mapping[str, str | int] | None = None,
) -> str:
    """Return the URL for a user's main page.

    Args:
        user_id (str): user ID
        venue_id (str): venue ID
        brewery_id (str): brewery ID
        beer_id (str|int): beer ID
        search (bool): whether to search
        page (str): specific page
        query (dict[str, str]|None): filter for page

    Returns:
        str: url to load to get user's main page
    """
    base = UNTAPPD_BASE_URL

    if user_id:
        base += f"user/{user_id}"
    elif venue_id:
        base += f"venue/{venue_id}"
    elif brewery_id:
        base += f"brewery/{brewery_id}"
    elif beer_id:
        base += f"beer/{beer_id}"
    elif search:
        base += "search"
    if page:
        if not base.endswith("/"):
            base += "/"
        base += f"{page.strip('/')}"

    base = base.strip("/")

    url = URL(base)

    if query:
        url = url.copy_merge_params(query)

    return str(url)


def make_soup(url: str) -> tuple[BeautifulSoup, bool]:
    """Fetch a page and return the soup.

    Args:
        url (str): URL to fetch

    Returns:
        tuple[BeautifulSoup, bool]: soup object and whether it was from cache
    """
    resp = client.get(url, timeout=10)
    resp.raise_for_status()

    logger.debug("Making soup from {}", url)

    return BeautifulSoup(resp.text, "html.parser"), resp.extensions.get("from_cache", False)


def id_from_href(element: Element) -> int:
    """Extract last past of a URL, which is an ID.

    Args:
        element (Element): element to extract href from

    Raises:
        ValueError: last part of url wasn't an integer

    Returns:
        int: last part of href, which is an id
    """
    last_bit: str = slug_from_href(element)
    try:
        return int(last_bit)
    except ValueError as excp:  # pragma: no cover
        msg = f"Cannot extract integer id from {last_bit=} element ({element.html})"
        raise ValueError(msg) from excp


def slug_from_href(element: Element) -> str:
    """Extract last past of a URL, which is a slug.

    Args:
        element (Element): element to extract href from

    Returns:
        str: last part of href
    """
    href: str = element.attrs["href"].removesuffix("/")
    return href.rpartition("/")[-1]


def end_of_href(tag: Tag) -> str | None:
    """Extract last past of a URL, which is a slug.

    Args:
        tag (Tag): html element containing an href

    Returns:
        str: last part of href
    """
    href = (tag.a and tag.a.get("href")) or tag.get("href")

    if not href or "/" not in href:
        logger.debug("No href found in element: {}", tag)
        return None

    href = str(href).removesuffix("/")

    return href.rpartition("/")[-1]


def date_from_details(details: Tag) -> datetime | None:
    """Extract a date that may be present.

    Args:
        details (Tag): html element containing date

    Returns:
        datetime: parsed date
    """
    dt = details.select_one(".date-time")

    return parse_date(dt.text) if dt else None


def date_from_data_href(
    element: Element, label: str, *, date_only: bool = False
) -> datetime | None:
    """Extract a date that may be present.

    Args:
        element (Element): html element containing date
        label (str): data-href value
        date_only (bool): only parse the date (not the time)?

    Returns:
        datetime: parsed date
    """
    if href := element.find(f'.date [data-href="{label}"]', first=True):
        dt = parse_date(href.text).astimezone()  # pyright: ignore[reportAttributeAccessIssue]
        return dt.date() if date_only else dt  # pyright: ignore[reportReturnType]
    return None


def parse_abv(abv_data: str) -> float | None:
    """Parse the ABV data buried in text.

    Args:
        abv_data (str): text version, eg '7.5% ABV'

    Returns:
        float: ABV as a number
    """
    parsed_abv = parse.search("{:g}%", abv_data)
    if not isinstance(parsed_abv, parse.Result):
        return None  # pragma: no cover

    try:
        return float(parsed_abv[0])
    except TypeError:  # pragma: no cover
        return None


def parse_ibu(ibu_data: str) -> int | None:
    """Parse the IBU data buried in text.

    Args:
        ibu_data (str): text version, eg '15 IBU'

    Returns:
        int: IBU as a number
    """
    parsed_ibu = parse.search("{:d} IBU", ibu_data)
    if not isinstance(parsed_ibu, parse.Result):
        return None  # pragma: no cover

    try:
        return int(parsed_ibu[0])
    except TypeError:  # pragma: no cover
        return None


def parsed_value(fmt: str, string: str) -> int | float | None:
    """Search for a value in a string and return it.

    Args:
        fmt (str): parse module's format string
        string (str): string to search for fmt pattern

    Returns:
        found value, if any
    """
    match = parse.search(fmt, string)
    return match[0] if isinstance(match, parse.Result) else None


def parse_rating(which: str, ratings: str) -> float | None:
    """Find the requested rating in the supplied string.

    Args:
        which (str): which rating to look for
        ratings (str): full rating string with all ratings

    Returns:
        float: rating found, if any
    """
    ratings_match = parse.search(which + " rating ({:g})", ratings)
    return ratings_match[0] if ratings_match else None  # pyright: ignore[reportIndexIssue]


def get_text(soup: BeautifulSoup | Tag, selector: str) -> str:
    """Get text from a soup element.

    Args:
        soup (BeautifulSoup): soup to search
        selector (str): CSS selector to find

    Returns:
        str: text found
    """
    el = soup.select_one(selector)
    return el.text.strip() if el else ""


def extract_checkin_elements_bs4(tag: Tag) -> tuple[Tag, Tag, Tag, Tag | None]:
    """Extract four linked elements in a checkin.

    Args:
        tag (Tag): checkin element

    Raises:
        ValueError: element passed didn't contain 3-4 <a> tags

    Returns:
        tuple[Tag, Tag, Tag, Tag]: user, beer, brewery, location
    """
    elements = tag.select(".top .text a")

    if len(elements) == 3:  # noqa: PLR2004
        return (elements[0], elements[1], elements[2], None)
    if len(elements) == 4:  # noqa: PLR2004
        return (elements[0], elements[1], elements[2], elements[3])

    msg = f"Wanted 3 or 4 <a> elements (not {len(elements)}) in {tag}"
    raise ValueError(msg)
