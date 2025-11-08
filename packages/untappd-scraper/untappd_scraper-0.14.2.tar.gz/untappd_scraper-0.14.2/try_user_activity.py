"""Set up expectations for untappd-scraper API."""
from __future__ import annotations

from untappd_scraper.user import User

users = ["fadell"]
# users = ["mw1414", "Svety_T", "fadell"]

for user_id in users:
    user = User(user_id)
    print(f"\n{user.name=}")

    for checkin in user.activity():
        print(f"\n\t{checkin.name=}\n\t\t{checkin}")

    # menus = venue.menus()
    # for menu in menus:
    #     print(f"\n\t{menu.selection=} / {menu.name=}")

    #     for beer in menu.beers:
    #         print(f"\t\t{beer.name=}")
