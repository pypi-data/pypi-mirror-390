"""Set up expectations for untappd-scraper API."""

from __future__ import annotations

from untappd_scraper.user import User
from untappd_scraper.venue import Venue

user_ids = ["mw1414", "emmlikesbeer"]
for user_id in user_ids:
    user = User(user_id)
    print(f"\n{user.name=} {user.total_uniques=}\t{user.location=}")  # noqa: T201

    checkins = user.activity()
    last_checkin = checkins[0]
    last_venue = last_checkin.location_id
    print(f"{last_venue=}")  # noqa: T201
    assert last_venue

    venue = Venue(venue_id=last_venue)
    print(f"{venue.name=} {venue.location=}")  # noqa: T201
