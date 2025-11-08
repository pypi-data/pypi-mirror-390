"""Set up expectations for untappd-scraper API."""
from __future__ import annotations

from untappd_scraper.venue import Venue

venue_ids = [
    14705,  # 4 pines
    107565,  # sweeney's
]
for venue_id in venue_ids:
    venue = Venue(venue_id)
    print(f"\n{venue.name=} {venue.verified=}\t{venue.categories=}")
