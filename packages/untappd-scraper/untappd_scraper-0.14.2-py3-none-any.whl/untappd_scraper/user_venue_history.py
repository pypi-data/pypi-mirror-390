"""Untappd user venue history functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from utpd_models_web.venue import WebUserHistoryVenue

from untappd_scraper.html_session import get
from untappd_scraper.web import date_from_data_href, id_from_href, parsed_value, url_of

if TYPE_CHECKING:  # pragma: no cover
    from requests_html import Element


def load_user_venue_history(user_id: str) -> list[WebUserHistoryVenue]:
    """Load all availble recent venues for a user.

    Args:
        user_id (str): user ID to load

    Returns:
        Collection[WebUserHistoryVenue]: last 15 (or so) visited venues
    """
    resp = get(url_of(user_id, page="venues", query={"sort": "recent"}))  # pyright: ignore[reportArgumentType]

    return [recent_venue_details(checkin) for checkin in resp.html.find(".venue-item")]  # pyright: ignore[reportGeneralTypeIssues, reportFunctionMemberAccess]


def recent_venue_details(recent: Element) -> WebUserHistoryVenue:
    """Extract venue details from a venue history entry.

    Args:
        recent (Element): single venue

    Returns:
        WebUserHistoryVenue: Interesting details for a venue
    """
    category = recent.find(".category", first=True).text
    address = recent.find(".address", first=True).text

    is_verified = recent.find(".verified", first=True) is not None

    details = recent.find(".details", first=True)

    # TODO merge
    first_visit = date_from_data_href(details, ":firstVisit", date_only=True)
    last_visit = date_from_data_href(details, ":lastVisit", date_only=True)
    assert last_visit  # must have this one ... maybe not first though

    first_visit_el = details.find('.date [data-href=":firstVisit"]', first=True)
    first_checkin = id_from_href(first_visit_el) if first_visit_el else None
    last_visit_el = details.find('.date [data-href=":lastVisit"]', first=True)
    last_checkin = id_from_href(last_visit_el) if last_visit_el else None

    checkins = parsed_value("Check-ins: {:d}", details.find(".check-ins", first=True).text)

    return WebUserHistoryVenue(
        venue_id=int(recent.attrs["data-venue-id"]),
        name=recent.find(".name a", first=True).text,
        url=recent.find(".name a", first=True).absolute_links.pop(),
        category=category,
        address=address,
        is_verified=is_verified,
        first_visit=first_visit,
        last_visit=last_visit,
        num_checkins=checkins,
        first_checkin_id=first_checkin,
        last_checkin_id=last_checkin,
    )
