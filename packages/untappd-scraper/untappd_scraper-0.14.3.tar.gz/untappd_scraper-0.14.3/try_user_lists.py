"""Set up expectations for untappd-scraper API."""
from __future__ import annotations

from untappd_scraper.user import User

users = ["jimmy-swings", "lightbeerking", "mw1414"]

for user_id in users:
    user = User(user_id)
    print(f"\n{user.name=}")

    for user_list in user.lists():
        print(
            "\t",
            user_list.name,
            user_list.description,
            user_list.is_wishlist,
            # len(user_list.beers),
            # "of",
            user_list.num_items,
            # user_list.full_scrape,
        )
        # for beer in user_list.beers:
        #     print(beer)

    if user_id == "jimmy-swings":
        ll = user.lists_detail("fridge")
        print(ll)
    elif user_id == "lightbeerking":
        ll = user.lists_detail("fridge")
        print(ll)
