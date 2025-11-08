"""Set up expectations for untappd-scraper API."""

from __future__ import annotations

from datetime import datetime

from untappd_scraper.logging_config import configure_logging
from untappd_scraper.user import User

logger = configure_logging(__name__)  # , logging.DEBUG)


users = ["gregavola"]

for user_id in users:
    user = User(user_id)
    print(f"\n{user.name=}")

    for checkin in user.activity():
        print(f"\n\t{checkin.name=}\n\t\t{checkin}")

    print("\n\nLists:")

    for userlist in user.lists():
        print(f"\n\t{userlist.name=} {userlist.num_items=}")

    print("\n\nRecent Venues:")

    for venue in user.venue_history():
        ago = datetime.now().date() - venue.last_visit
        print(
            f"\n\t{venue.name=} {venue.last_visit.strftime('%b %d %Y')} "
            + f"({ago.days} days ago)"
        )

    print("\n\nRecent Uniques:")

    for beer in user.beer_history():
        print(f"\t{beer}, {beer.total_checkins=}")
