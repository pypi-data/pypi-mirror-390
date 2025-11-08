"""Set up expectations for untappd-scraper API."""

from __future__ import annotations

from untappd_scraper.venue import Venue

for which_venue in (14705, "hotel sweeney", "4 pines truckbar"):  # 4 pines
    venue = (
        Venue(which_venue) if isinstance(which_venue, int) else Venue.from_name(which_venue)
    )
    if not venue:
        continue

    print(f"\n\n{venue.name}\n")  # noqa: T201
    print(*sorted(venue.activity(), key=lambda ven: ven.checkin), sep="\n")  # noqa: T201
