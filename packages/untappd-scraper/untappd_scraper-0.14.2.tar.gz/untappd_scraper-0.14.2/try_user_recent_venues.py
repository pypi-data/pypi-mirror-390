"""Set up expectations for untappd-scraper API."""
from __future__ import annotations

from untappd_scraper.user import User

users = ["mw1414", "Svety_T"]

for user_id in users:
    user = User(user_id)
    print(f"\n{user.name=}")

    for venue in user.venue_history():
        print("\t", venue)
        # print(f"\n\t{checkin.name=}\n\t\t{checkin}")

    # menus = venue.menus()
    # for menu in menus:
    #     print(f"\n\t{menu.selection=} / {menu.name=}")

    #     for beer in menu.beers:
    #         print(f"\t\t{beer.name=}")
