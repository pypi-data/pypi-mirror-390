"""Set up expectations for untappd-scraper API."""

from __future__ import annotations

from untappd_scraper.logging_config import configure_logging
from untappd_scraper.venue import Venue

logger = configure_logging(__name__)  # , logging.INFO)

# venue_ids = [
#     14705,  # 4 pines
#     99967,  # collaroy
# ]

# for venue_id in venue_ids:
#     venue = Venue(venue_id)
#     print(f"\n{venue.name=}")

#     for num, checkin in enumerate(venue.activity(), start=1):
#         print(f"\n\t{num=}\t{checkin.name=}\n\t\t{checkin}")
#         if num > 5:
#             break  # that's enough for demo

venues = {
    "collaroy beach club",
    "nomad transit",
    "iron duke",
    "noble hops",
    "hotel sweeney",
    "winona manly",
    "beer cartel",
    "yardhouse waikiki",
}

for venue_name in venues:
    venue = Venue.from_name(venue_name)

    if not venue:
        print(f"Can't find {venue_name}")
        continue

    print(f"\n{venue.name=} {venue.address=} {venue.verified=}\t{venue.categories=}\n")
    print("\n".join([str(beer) for beer in venue.activity()]))

    for menu in venue.menus():
        print(f"\n{menu.selection=} / {menu.name=}")

        print("\n\t\t", end="")
        print("\n\t\t".join(str(beer) for beer in menu.beers))


# venue = Venue.from_name("hotel sweeney")
# print(f"\n{venue.name=} {venue.verified=}\t{venue.categories=}\n")
# print("\n".join([str(beer) for beer in venue.activity()]))

# for menu in venue.menus():
#     print(f"\n{menu.selection=} / {menu.name=}")

#     print("\n\t\t", end="")
#     print("\n\t\t".join(str(beer) for beer in menu.beers))

# for beer in sorted(menu.beers, key=sort_by_global_rating, reverse=True):
#     print(f"\t\t{beer}")


# """Set up expectations for untappd-scraper API."""
# from __future__ import annotations

# from untappd_scraper.venue import Venue

# venue_ids = [
#     14705,  # 4 pines
#     107565,  # sweeney's
# ]
# for venue_id in venue_ids:
#     venue = Venue(venue_id)
#     print(f"\n{venue.name=} {venue.verified=}\t{venue.categories=}")
# """Set up expectations for untappd-scraper API."""
# from __future__ import annotations

# from untappd_scraper.structs.web import WebVenueMenuBeer
# from untappd_scraper.venue import Venue


# def sort_by_global_rating(beer: WebVenueMenuBeer) -> float:
#     """Extract the beer's global rating, for sorting.

#     Args:
#         beer (WebVenueMenuBeer): beer to inspect

#     Returns:
#         float: global rating
#     """
#     return beer.global_rating or 0


# venues = [
#     14705,  # 4 pines
#     99967,  # collaroy
#     107565,  # sweeney's
#     8931121,  # winona
#     112700,  # beer cartel
# ]

# for venue_id in venues:
#     venue = Venue(venue_id)
#     print(f"\n{venue.name=}")

#     menus = venue.menus()
#     for menu in menus:
#         print(f"\n\t{menu.selection=} / {menu.name=}")

#         for beer in sorted(menu.beers, key=sort_by_global_rating, reverse=True):
#             print(f"\t\t{beer}")
