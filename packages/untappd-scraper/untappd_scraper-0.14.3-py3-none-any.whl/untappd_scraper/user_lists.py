"""Untappd user list functions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import TYPE_CHECKING, Final

import parse
from dateutil.parser import parse as parse_date

from untappd_scraper.html_session import get
from untappd_scraper.user_lists_details import WebUserListBeerDetails, parse_more_details
from untappd_scraper.web import id_from_href, parse_abv, parse_ibu, url_of

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Collection, Iterator, Sequence
    from datetime import datetime

    from requests_html import HTMLResponse


@dataclass(frozen=True)
class WebUserListBeer:
    """Beer visible inside a user's list web page."""

    beer_id: int
    name: str = field(compare=False)
    brewery: str = field(compare=False)
    style: str = field(compare=False)
    added: datetime = field(compare=False)
    global_rating: float | None = field(compare=False, default=None)
    abv: float | None = field(compare=False, default=None)
    ibu: int | None = field(compare=False, default=None)
    details: WebUserListBeerDetails | None = field(compare=False, default=None)

    @classmethod
    def from_html(cls, html: HTMLResponse) -> WebUserListBeer:
        """Construct from parsed html object.

        Args:
            html (HTMLResponse): single beer from a list section

        Returns:
            WebUserListBeer: populated details of a users list
        """
        beer_id = id_from_href(html.find("a", first=True))
        beer_name = html.find(".item-info h2", first=True).text
        brewery_name = html.find(".item-info h3", first=True).text
        style, abv, ibu = html.find("h4")[0].text.split(" • ")
        abv = parse_abv(abv)
        ibu = parse_ibu(ibu)
        added = parse_date(
            html.find(".date-added .format-date", first=True).attrs["data-date"]
        )
        try:
            rating = float(html.find(".rating-container div", first=True).attrs["data-rating"])
        except AttributeError:
            rating = None

        more_details = parse_more_details(html.find(".item-info-more", first=True))

        return cls(
            beer_id=beer_id,
            name=beer_name,
            brewery=brewery_name,
            style=style,
            added=added,
            global_rating=rating,
            abv=abv,
            ibu=ibu,
            details=more_details,
        )


@dataclass(frozen=True)
class WebUserList:
    """A row in a user's list web page."""

    username: str
    name: str
    description: str = field(compare=False)
    num_items: int = field(compare=False)
    updated: datetime | None = field(compare=False)
    url: str = field(compare=False)
    beers: set[WebUserListBeer] = field(compare=False, repr=False, default_factory=set)

    @property
    def is_wishlist(self) -> bool:
        """Return if this is a wish list, vs a user list.

        Returns:
            bool: is a wish list
        """
        return self.url.endswith("/wishlist")

    @property
    def full_scrape(self) -> bool | None:
        """Return if all beers on a list were scraped.

        Returns:
            bool: we got all beers
        """
        return len(self.beers) >= self.num_items

    @classmethod
    def from_html(cls, html: HTMLResponse) -> WebUserList:
        """Construct from parsed html object.

        Args:
            html (HTMLResponse):single list section from Lists page

        Returns:
            WebUserList: populated details of a users list
        """
        username = re.findall("user/([^/]+)/lists", html.url)[0]
        listname = html.find("div.item-info h2", first=True).text
        try:
            desc = html.xpath("//a/div[2]/h3[1]/text()")[0]
        except IndexError:
            desc = ""
        num_items_str = html.find("div.item-info h4", first=True).text
        num_items = parse.search("{:d} Item", num_items_str)[0]
        try:
            updated_str = html.find("div.item-info h4 abbr", first=True).attrs["data-date"]
        except AttributeError:
            updated: datetime | None = None
        else:
            updated = parse_date(updated_str)
        url = html.absolute_links.pop()

        return cls(
            username=username,
            name=listname,
            description=desc,
            num_items=num_items,
            updated=updated,
            url=url,
        )


def load_user_lists(user_id: str) -> list[WebUserList]:
    """Load user's list page and scrape all lists and their visible beers.

    Args:
        user_id (str): user ID to load

    Returns:
        list[WebUserList]: all visible lists populated with their visible beers
    """
    lists_page_url = url_of(user_id, page="lists")
    resp = get(lists_page_url)

    return [WebUserList.from_html(list_html) for list_html in resp.html.find(".single-list")]


def scrape_list_beers(user_list: WebUserList) -> Collection[WebUserListBeer]:
    """Scrape the actual list page to get all (or as many as possible of) the beers.

    Utilise opposite sort ordering and filtering to grab as many as possible,
    15 at a time.

    Args:
        user_list (WebUserList): single user list object to update

    Returns:
        Collection[WebUserListBeer]: all beers we could scrape for this list
    """
    beers: set[WebUserListBeer] = set()
    # - scrape every useful sort order of the main list
    for list_sort_html in list_page_all_sorts(user_list.url):
        beers.update(extract_list_beers(list_sort_html))

        if len(beers) >= user_list.num_items:
            return beers

    return beers  # pragma: no cover  # XXX

    # - didn't get all?
    # -
    # 2. count
    # identify missing beers
    # 3.

    # First try sorting in A-Z Z-A type order pairs

    # Still don't have them all. Try different beer filtering
    # for list_filter_html in filtered_list_pages(user_list):
    #     print(list_filter_html.url)  # XXX
    #     user_list.beers.update(extract_list_beers(list_filter_html))
    #     print("now got", len(user_list.beers), "of", user_list.num_items)

    #     if user_list.full_scrape:
    #         # print("should return")  # XXX
    #         return
    # for picker in ("style", "brewery"):
    # pass


def list_page_all_sorts(url: str) -> Iterator[HTMLResponse]:  # pragma: no cover
    """Return all useful sorted versions of page.

    Args:
        url (str): URL to start at

    Yields:
        Iterator[HTMLResponse]: page with all useful sorts applied
    """
    resp = get(url)
    return (get(url, params={"sort": sort_key}) for sort_key in page_sort_orders(resp.html))


USEFUL_SORTS_KEYS: Final[Sequence[str]] = (
    "date_asc",
    "date",
    "beer_name_asc",
    "beer_name_desc",
    "brewery_name_asc",
    "brewery_name_desc",
    "highest_abv",
    "lowest_abv",
    "highest_rated",
    "lowest_rated",
    "lowest_ibu",
    "highest_ibu",
    "style_name_asc",
    "style_name_desc",
    "quantity_asc",
    "quantity_desc",
)


def page_sort_orders(
    list_page: HTMLResponse, useful_sorts_keys: Sequence[str] = USEFUL_SORTS_KEYS
) -> Sequence[str]:
    """Return valid and useful sort keys for a list page.

    Args:
        list_page (HTMLResponse): list page
        useful_sorts_keys (Container[str]): useful sort keys to try. Optional

    Returns:
        Sequence[str]: valid and useful sort keys
    """
    page_sorts = {
        li.attrs["data-sort-key"] for li in list_page.find(".menu-sorting .sort-items")
    }

    return tuple(sort_key for sort_key in useful_sorts_keys if sort_key in page_sorts)


@lru_cache
def extract_list_beers(list_html: HTMLResponse) -> Iterator[WebUserListBeer]:
    """Extract each beer from a list page.

    Args:
        list_html (HTMLResponse): page with list beers

    Returns:
        Iterator[WebUserListBeer]: populated details
    """
    return (
        WebUserListBeer.from_html(beer_html) for beer_html in list_html.html.find(".list-item")
    )
