"""Untappd user functions."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import PurePosixPath
from typing import TYPE_CHECKING, Any

from dateutil.parser import parse as parse_date
from httpx import HTTPStatusError
from utpd_models_web.checkin import WebActivityBeer
from utpd_models_web.user import WebUserDetails

from untappd_scraper.logging_config import configure_logging, logger
from untappd_scraper.user_beer_history import (
    UserHistoryResponse,
    beer_history,
    brewery_history,
)
from untappd_scraper.user_lists import WebUserList, load_user_lists, scrape_list_beers
from untappd_scraper.user_venue_history import load_user_venue_history
from untappd_scraper.web import get_text, make_soup, url_of

if TYPE_CHECKING:
    from collections.abc import Collection

    from bs4 import BeautifulSoup, Tag
    from utpd_models_web.venue import WebUserHistoryVenue

configure_logging(__name__)

logger.info("Loading user...")


@dataclass
class User:
    """Untappd user."""

    user_id: str

    details: WebUserDetails = field(init=False, repr=False)
    activity: tuple[WebActivityBeer, ...] = field(init=False, repr=False)

    # Only populate these when requested
    _lists: list[WebUserList] = field(default_factory=list, init=False, repr=False)
    _venue_history: list[WebUserHistoryVenue] = field(
        default_factory=list, init=False, repr=False
    )

    _soup_user: BeautifulSoup = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialise a User object, storing the user ID and loading details.

        Raises:
            ValueError: if the user ID is invalid or the page cannot be loaded
        """
        url = url_of(user_id=self.user_id)

        try:
            self._soup_user, _ = make_soup(url)
        except HTTPStatusError as e:
            logger.debug("Error getting user page for {}: {}", self.user_id, e)
            msg = f"Invalid userid {self.user_id}"
            raise ValueError(msg) from e

        self.activity = user_activity(self._soup_user)
        self.details = user_details(self._soup_user, url=url)

        # Populate recent activity summary into user details
        recent_beers = {a.beer_id for a in self.activity}
        recent_venues = {a.location_id for a in self.activity if a.location_id}
        self.details = replace(
            self.details, recent_beers=list(recent_beers), recent_venues=list(recent_venues)
        )

    @property
    def user_name(self) -> str:
        """Return the user's name."""
        return self.details.name

    def beer_history(self) -> UserHistoryResponse:
        """Scrape last 25 (or so) of a user's uniques.

        Returns:
            UserHistoryResponse: user's recent uniques
        """
        return beer_history(self.user_id)

    def brewery_history(self, brewery_id: int, max_resorts: int = 0) -> UserHistoryResponse:
        """Scrape as many of a user's uniques as possible from a brewery.

        Args:
            brewery_id (int): brewery id to filter by
            max_resorts (NumReSorts): number of times to re-sort the list to get more uniques

        Returns:
            UserHistoryResponse: user's uniques
        """
        return brewery_history(
            user_id=self.user_id, brewery_id=brewery_id, max_resorts=max_resorts
        )

    def lists(self) -> list[WebUserList]:
        """Scrape user's list page and return all visible listed beers.

        Returns:
            Collection[WebUserList]: all user's lists with 15 (or so) visible beers
        """
        if not self._lists:
            self._lists = load_user_lists(self.user_id)

        return self._lists

    def lists_detail(self, list_name: str) -> list[WebUserList]:
        """Return populated details of a user's list.

        Args:
            list_name (str): list name (or part thereof, case-insensitive)

        Returns:
            list[WebUserList]: matching lists with detail filled in
        """
        matching = [
            user_list
            for user_list in self.lists()
            if list_name.casefold() in user_list.name.casefold()
        ]

        for user_list in matching:
            user_list.beers.update(scrape_list_beers(user_list))

        return matching

    def venue_history(self) -> Collection[WebUserHistoryVenue]:
        """Scrape last 25 (or so) of a user's visited venues.

        Returns:
            Collection[WebUserHistoryVenue]: user's recent venues
        """
        if not self._venue_history:
            self._venue_history = load_user_venue_history(self.user_id)

        return self._venue_history

    def __getattr__(self, name: str) -> Any:  # noqa: ANN401
        """Return unknown attributes from user details.

        Args:
            name (str): attribute to lookup

        Returns:
            Any: attribute value
        """
        return getattr(self.details, name)


# ----- user details processing -----


def user_details(soup: BeautifulSoup, *, url: str) -> WebUserDetails:
    """Parse a user's main page into user details.

    Args:
        soup (BeautifulSoup): user's main page parsed
        url (str): URL of the user's page

    Returns:
        WebUserDetails: general user details
    """
    user_info = soup.select_one(".user-info .info")
    assert user_info, "User info tag not found"

    user_name = get_text(user_info, "h1")
    user_id = e.text.strip() if (e := user_info.select_one(".user-details p.username")) else ""
    user_location = (
        e.text.strip() if (e := user_info.select_one(".user-details p.location")) else ""
    )

    stats = soup.select_one(".stats")
    assert stats, "Stats tag not found"

    total_beers = (
        e.text if (e := stats.select_one('[data-href=":stats/general"] span')) else "0"
    )
    total_uniques = (
        e.text if (e := stats.select_one('[data-href=":stats/beerhistory"] span')) else "0"
    )
    total_badges = (
        e.text if (e := stats.select_one('[data-href=":stats/badges"] span')) else "0"
    )
    total_friends = (
        e.text if (e := stats.select_one('[data-href=":stats/friends"] span')) else "0"
    )

    return WebUserDetails(
        user_id=user_id,
        name=user_name,
        location=user_location,
        url=url,
        total_beers=str_to_int(total_beers),
        total_uniques=str_to_int(total_uniques),
        total_badges=str_to_int(total_badges),
        total_friends=str_to_int(total_friends),
    )


def user_activity(soup: BeautifulSoup) -> tuple[WebActivityBeer, ...]:
    """Parse a user's main page into checkins.

    Args:
        soup (BeautifulSoup): user's main page parsed

    Returns:
        tuple[WebActivityBeer, ...]: user's recent checkins
    """
    div = soup.select_one("div#main-stream")
    assert div, "Main stream tag not found"

    activities = div.select(".checkin")

    return tuple(parse_activity(activity) for activity in activities)


def parse_activity(activity: Tag) -> WebActivityBeer:
    """Parse a single activity item into a WebActivityBeer object."""
    checkin_link = activity.select_one("div.bottom a")
    assert checkin_link, "Checkin link tag not found"
    checkin_time = parse_date(checkin_link.text)
    assert checkin_time.tzinfo, "Checkin time does not have timezone info"

    top = activity.select_one("div.top")
    assert top, "Top tag not found"
    user_tag = top.select_one("p.text > a:nth-child(1)")
    assert user_tag, "User tag not found"
    beer_tag = top.select_one("p.text > a:nth-child(2)")
    assert beer_tag, "Beer tag not found"
    label_url = str(e["src"]) if (e := top.select_one("a img")) else ""
    brewery_tag = top.select_one("p.text > a:nth-child(3)")
    assert brewery_tag, "Brewery tag not found"
    location_tag = top.select_one("p.text > a:nth-child(4)")
    purchased_tag = top.select_one("p.purchased a")
    if rating_tag := top.select_one("div.caps[data-rating]"):
        data_rating = rating_tag["data-rating"]
        assert isinstance(data_rating, str), "Rating data is not a string"
        data_rating = float(data_rating)
    else:
        data_rating = None
    friends_tag = top.select_one("div.tagged-friends")
    friends = extract_friends(friends_tag)

    return WebActivityBeer(
        checkin_id=int(href_base(checkin_link)),
        checkin=checkin_time,
        user_name=href_base(user_tag),
        beer_name=beer_tag.text.strip(),
        beer_id=int(href_base(beer_tag)),
        beer_label_url=label_url,
        brewery_name=brewery_tag.text.strip(),
        brewery_id=None,  # not supplied in the activity
        brewery_url=href_base(brewery_tag),
        location=location_tag.text.strip() if location_tag else None,
        location_id=int(href_base(location_tag)) if location_tag else None,
        purchased_at=purchased_tag.text.strip() if purchased_tag else None,
        purchased_id=int(href_base(purchased_tag)) if purchased_tag else None,
        comment=e.text.strip() if (e := top.select_one("p.comment-text")) else None,
        serving=e.text.strip() if (e := top.select_one("p.serving")) else None,
        user_rating=data_rating,
        friends=friends,
    )


def str_to_int(numeric_string: str) -> int:
    """Convert a string to an integer.

    Args:
        numeric_string (str): amount with commas

    Returns:
        int: value as an integer
    """
    return int(numeric_string.replace(",", ""))


def href_base(link: Tag | None) -> str:
    """Extract the last bit from a link.

    Args:
        link (Tag): link element, with href="/a/b/123" for example

    Returns:
        str: ID extracted from the link
    """
    if not link:
        msg = "No link provided to href_base"
        logger.error(msg)
        raise ValueError(msg)

    href = link.get("href", "")
    assert isinstance(href, str), "Link href is not a string"

    return PurePosixPath(href).name


def extract_friends(friends_tag: Tag | None) -> list[str] | None:
    """Extract friends from a friends tag.

    Args:
        friends_tag (Tag | None): tag containing friends

    Returns:
        list[str] | None: list of friend names or None if no friends
    """
    if not friends_tag:
        return None

    return [href_base(friend) for friend in friends_tag.select("a") if href_base(friend)]
