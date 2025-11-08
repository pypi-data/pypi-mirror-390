"""Set up expectations for untappd-scraper API."""

from __future__ import annotations

from typing import TYPE_CHECKING

from untappd_scraper.logging_config import configure_logging
from untappd_scraper.venue import Venue

if TYPE_CHECKING:  # pragma: no cover
    from untappd_scraper.structs.web import WebVenueMenuBeer

logger = configure_logging(__name__)  # , logging.DEBUG)


def sort_by_global_rating(beer: WebVenueMenuBeer) -> float:
    """Extract the beer's global rating, for sorting.

    Args:
        beer (WebVenueMenuBeer): beer to inspect

    Returns:
        float: global rating
    """
    return beer.global_rating or 0


venues = [
    # 14705,  # 4 pines
    # 99967,  # collaroy
    107565  # sweeney's
    # 8931121,  # winona
    # 112700,  # beer cartel
    # 2010178  # nomad
]

for venue_id in venues:
    venue = Venue(venue_id)
    print(f"\n{venue.name=}")  # noqa: T201

    menus = venue.menus()
    for menu in menus:
        print(f"\n\t{menu.selection=} / {menu.name=}")  # noqa: T201

        for beer in sorted(menu.beers, key=sort_by_global_rating, reverse=True):
            print(f"\t\t{beer}\t{beer.abv=} {beer.ibu=} {beer.brewery_id=}")  # noqa: T201
