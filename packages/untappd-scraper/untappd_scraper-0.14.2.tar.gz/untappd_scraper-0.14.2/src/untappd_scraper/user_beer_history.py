"""Untappd user beer history functions."""

from __future__ import annotations

import dataclasses
import logging
import random
import re
import time
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import urljoin

import parse
from pydantic import BaseModel, ConfigDict, computed_field
from utpd_models_web.beer import WebUserHistoryBeer
from utpd_models_web.constants import UNTAPPD_BASE_URL, UNTAPPD_BEER_HISTORY_SIZE

from untappd_scraper.logging_config import logger
from untappd_scraper.web import (
    date_from_details,
    end_of_href,
    make_soup,
    parse_abv,
    parse_ibu,
    parse_rating,
    url_of,
)

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Iterable, Sequence

    from bs4 import BeautifulSoup, Tag


logging.getLogger("parse").setLevel(logging.INFO)

logger.info("Loading user beer history...")


def parse_web_user_history_beer(beer_item: Tag) -> WebUserHistoryBeer:
    """Parse beer details from a scraped history beer."""
    bid = int(str(beer_item["data-bid"]))

    if name_el := beer_item.select_one(".beer-details p.name a"):
        name = str(name_el.text).strip()
        url = urljoin(UNTAPPD_BASE_URL, str(name_el["href"]))
    else:  # pragma: no cover
        name = ""
        url = None

    label = str(img.get("src", "")) if (img := beer_item.select_one("a img")) else ""

    # Brewery
    brewery_el = beer_item.select_one(".beer-details p.brewery a")
    brewery_name = str(brewery_el.text.strip() if brewery_el else "")
    brewery_url = str(brewery_el["href"]).strip("/") if brewery_el else ""
    brewery_id = int(match[1]) if (match := re.search(r"/(\d+)$", brewery_url)) else None

    # Style
    style_el = beer_item.select_one(".beer-details p.style")
    style = str(style_el.text.strip() if style_el else "")

    # First/Recent check-in dates
    date_els = beer_item.select(".details p.date")
    if len(date_els) == 2:  # noqa: PLR2004
        first, recent = date_els

        first_checkin = date_from_details(first)
        recent_checkin = date_from_details(recent)
        first_checkin_id = int(end_of_href(first) or 0)
        recent_checkin_id = int(end_of_href(recent) or 0)
    else:  # pragma: no cover
        first_checkin = None
        first_checkin_id = None
        recent_checkin = None
        recent_checkin_id = None

    total_checkins = 0
    total_el = beer_item.select_one(".details p.check-ins")
    if total_el and (total := parse.search("Total: {:d}", str(total_el.text))):
        assert isinstance(total, parse.Result)
        total_checkins = total[0]

    # Ratings
    if ratings := beer_item.select_one(".ratings"):
        user_rating = parse_rating("their", ratings.text)
        global_rating = parse_rating("global", ratings.text)
    else:  # pragma: no cover
        user_rating = None
        global_rating = None

    # ABV
    abv_el = beer_item.select_one(".details p.abv")
    abv = parse_abv(str(abv_el.text)) if abv_el else None

    # IBU
    ibu_el = beer_item.select_one(".details p.ibu")
    ibu = parse_ibu(str(ibu_el.text)) if ibu_el else None

    return WebUserHistoryBeer(
        beer_id=bid,
        beer_name=name,
        beer_label_url=label,
        brewery_id=brewery_id,
        brewery_name=brewery_name,
        brewery_url=brewery_url,
        style=style,
        url=url,
        first_checkin=first_checkin or datetime.min,
        first_checkin_id=first_checkin_id or 0,
        recent_checkin=recent_checkin or datetime.min,
        recent_checkin_id=recent_checkin_id or 0,
        total_checkins=total_checkins,
        user_rating=user_rating,
        global_rating=global_rating,
        abv=float(abv) if abv else None,
        ibu=ibu,
    )


# Use Pyandtic to later interface with FastAPI and friends
class UserHistoryResponse(BaseModel):
    """Response for user beer history."""

    model_config = ConfigDict(frozen=True)

    total_expected: int
    results: list[WebUserHistoryBeer]

    @computed_field
    @property
    def total_found(self) -> int:
        """Return number of beers found."""
        return len(self.results)

    @computed_field
    @property
    def found_all(self) -> bool:
        """Return True if we found all beers."""
        return self.total_found >= self.total_expected

    def __repr__(self) -> str:
        """Don't show all the beers. There's heaps."""
        return (
            f"{self.__class__.__name__}("
            f"total_expected={self.total_expected}, "
            f"total_found={self.total_found}, "
            f"found_all={self.found_all}"
            ")"
        )


UserHistoryResponse.model_rebuild()


def beer_history(user_id: str) -> UserHistoryResponse:
    """Scrape the beer history of a user.

    This is expected to be the last 25 unique beers they've had.
    """
    soup, _ = make_soup(url_of(user_id, page="beers"))

    if stats := soup.select_one("div.stats a[data-href=':user/beerhistory'] span.stat"):
        total_uniques = int(stats.text.replace(",", ""))
    else:  # pragma: no cover
        total_uniques = UNTAPPD_BEER_HISTORY_SIZE

    return UserHistoryResponse(
        total_expected=total_uniques,
        results=[parse_web_user_history_beer(item) for item in soup.select(".beer-item")],
    )


def brewery_history(
    user_id: str, brewery_id: int, max_resorts: int = 0, *, switch_to_style_scrape: int = 3
) -> UserHistoryResponse:
    """Scrape the beer history of a user for a specific brewery.

    This will agressively re-sort the list (if requested) to extract more uniques.
    It will also filter by style once the number of unfound beers reduces.

    Args:
        user_id (str): user ID to load
        brewery_id (int): brewery ID to filter by
        max_resorts (int): how many times to re-sort the list to get more uniques
        switch_to_style_scrape (int): if this many missing styles, switch to style scrape

    Returns:
        UserHistoryResponse: all found beers user has had from this brewery
    """
    soup, _ = make_soup(url_of(user_id, page="beers", query={"brewery_id": brewery_id}))

    # add 1 to re-sorts to include initial sort "date"
    sort_keys = extract_sort_keys(soup, num_keys=max_resorts + 1, exclude=["brewery"])
    beers_per_brewery = calc_beers_per_brewery(soup)
    beers_per_style, style_to_id = calc_beers_per_style(soup)
    total_for_brewery = beers_per_brewery.get(brewery_id, 0)
    logger.debug("Max re-sorts: {}, sort_keys: {}", max_resorts, sort_keys)
    logger.debug("Beers per brewery {}: {}", brewery_id, total_for_brewery)

    # The first page already has unique beers. Processing below is for re-sorts
    beers = {parse_web_user_history_beer(item) for item in soup.select(".beer-item")}

    if (
        len(beers) >= UNTAPPD_BEER_HISTORY_SIZE  # filled a page, there may be more
        and len(beers) < total_for_brewery  # not all beers
        and max_resorts  # user requested re-sorts
    ):
        beers, missing_styles = run_brewery_resorts(
            ReSortContext(user_id, brewery_id, sort_keys, beers, switch_to_style_scrape),
            total_for_brewery=total_for_brewery,
            beers_per_style=beers_per_style,
        )

        if missing_styles:
            logger.debug("Switching to style scraping. Missing styles: {}", missing_styles)

            beers = run_style_resorts(
                ReSortContext(user_id, brewery_id, sort_keys, beers, switch_to_style_scrape),
                missing_styles=missing_styles,
                style_to_id=style_to_id,
            )

    return UserHistoryResponse(
        total_expected=total_for_brewery, results=sorted(beers, key=lambda x: x.beer_id)
    )


@dataclasses.dataclass(frozen=True)
class ReSortContext:
    """Args passed around for re-sorting."""

    user_id: str
    brewery_id: int
    sort_keys: list[str]
    beers: set[WebUserHistoryBeer]
    switch_to_style_scrape: int


def run_brewery_resorts(
    context: ReSortContext, *, total_for_brewery: int, beers_per_style: dict[str, int]
) -> tuple[set[WebUserHistoryBeer], dict[str, int]]:
    """Run the brewery re-sorts to get more beers."""
    missing_styles: dict[str, int] = {}

    for sort_key in context.sort_keys:
        if sort_key == "date":
            continue  # already tried this one implicitly
        logger.debug("Trying sort key {}", sort_key)

        soup, from_cache = make_soup(
            url_of(
                context.user_id,
                page="beers",
                query={"brewery_id": context.brewery_id, "sort": sort_key},
            )
        )
        fetched = {parse_web_user_history_beer(item) for item in soup.select(".beer-item")}
        context.beers.update(fetched)
        logger.debug("Now got {} beers", len(context.beers))

        if len(context.beers) >= total_for_brewery:
            logger.debug("Got all beers for brewery {}", context.brewery_id)
            break

        missing_styles = calc_missing_styles(context.beers, beers_per_style)
        if len(missing_styles) <= context.switch_to_style_scrape:
            logger.debug("Switching to style scraping. Missing styles: {}", missing_styles)
            break

        if from_cache:
            logger.debug("Page was cached, so no need to sleep")
        else:
            logger.debug("sleeping...")
            time.sleep(random.uniform(1, 3))  # noqa: S311
            logger.debug("awake")

    return context.beers, missing_styles


def run_style_resorts(
    context: ReSortContext, *, missing_styles: dict[str, int], style_to_id: dict[str, int]
) -> set[WebUserHistoryBeer]:
    """Run the style re-sorts to get more beers."""
    # Don't want to go wild here. Let's just get the "n" most popular styles
    styles = sorted(missing_styles.items(), key=lambda x: x[1], reverse=True)
    styles = styles[: context.switch_to_style_scrape]
    logger.debug("Trying styles: {}", styles)

    for style, num_in_style in styles:
        logger.debug("Trying style {} with {} beers", style, num_in_style)
        for sort_key in context.sort_keys:
            logger.debug("Trying sort key {} for style {}", sort_key, style)
            soup, from_cache = make_soup(
                url_of(
                    context.user_id,
                    page="beers",
                    query={
                        "brewery_id": context.brewery_id,
                        "sort": sort_key,
                        "type_id": style_to_id[style],
                    },
                )
            )
            fetched = {parse_web_user_history_beer(item) for item in soup.select(".beer-item")}
            context.beers.update(fetched)
            logger.debug("Now got {} beers", len(context.beers))

            beers_of_style = sum(b.style == style for b in context.beers)
            if beers_of_style >= num_in_style:
                logger.debug("Got all beers of style {}", style)
                break

            if from_cache:
                logger.debug("Page was cached, so no need to sleep")
            else:
                logger.debug("sleeping...")
                time.sleep(random.uniform(1, 3))  # noqa: S311
                logger.debug("awake")

    logger.debug("Done with style scraping")

    return context.beers


def extract_sort_keys(
    soup: BeautifulSoup, num_keys: int, *, exclude: Sequence[str] = ()
) -> list[str]:
    """Extract the sort keys from the page.

    Args:
        soup (BeautifulSoup): soup object to parse
        num_keys (NumReSorts): how many sort keys to return
        exclude (Sequence[str]): sort keys to exclude

    Returns:
        list[str]: list of sort keys to try, based on effort
    """
    sorting = soup.select_one("ul.menu-sorting")
    if not sorting:
        return []  # pragma: no cover
    sort_keys = [str(item["data-sort-key"]) for item in sorting.select("li.sort-items")]

    # "date" is default, so move it to the front
    if "date_asc" in sort_keys:
        sort_keys.remove("date_asc")
        sort_keys.insert(0, "date_asc")
    if "date" in sort_keys:
        sort_keys.remove("date")
        sort_keys.insert(0, "date")

    # remove any sort that matches our exclude list
    to_remove = [key for key in sort_keys if any(key.startswith(excl) for excl in exclude)]
    for key in to_remove:
        sort_keys.remove(key)

    return sort_keys[:num_keys]


def calc_beers_per_brewery(soup: BeautifulSoup) -> dict[int, int]:
    """Calculate the number of beers per brewery based of the pull down option text.

    Tag looks like `<option value="4792">Hallertau Brewery (3)</option>`

    Args:
        soup (BeautifulSoup): soup object to parse. Should be main beer history page.

    Returns:
        dict[int, int]: brewery ID to number of beers
    """
    beers: dict[int, int] = {}

    options = soup.select("#brewery_picker option")

    for option in options:
        if option["value"] == "all":
            continue
        brewery_id = int(str(option["value"]))
        if brewery_count := parse.search(r"({:d})", str(option.text)):
            assert isinstance(brewery_count, parse.Result)
            beers[brewery_id] = int(brewery_count[0])

    return beers


def calc_beers_per_style(soup: BeautifulSoup) -> tuple[dict[str, int], dict[str, int]]:
    """Calculate the number of beers per style based of the pull down option text.

    Tag looks like `<option value="128">IPA - American (12)</option>`

    Args:
        soup (BeautifulSoup): soup object to parse. Should be main beer history page.

    Returns:
        tuple[dict[str, int], dict[str, int]]: style to # beers, style to ID
    """
    beers: dict[str, int] = {}
    id_of_style: dict[str, int] = {}

    options = soup.select("#style_picker option")

    for option in options:
        if option["value"] == "all":
            continue
        style_info = parse.parse("{style} ({count:d})", str(option.text))
        if isinstance(style_info, parse.Result):
            beers[style_info["style"]] = int(style_info["count"])
            id_of_style[style_info["style"]] = int(str(option["value"]))

    return beers, id_of_style


def calc_missing_styles(
    beers: Iterable[WebUserHistoryBeer], beers_per_style: dict[str, int]
) -> dict[str, int]:
    """Calculate how many beers per style have not yet been scraped.

    Args:
        beers (Iterable[WebUserHistoryBeer]): beers already scraped
        beers_per_style (dict[str, int]): number of beers per style user has had
    """
    return {
        style: expected
        for style, expected in beers_per_style.items()
        if sum(b.style == style for b in beers) < expected
    }
