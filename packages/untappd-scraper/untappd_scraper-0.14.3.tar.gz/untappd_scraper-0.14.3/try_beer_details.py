"""Set up expectations for untappd-scraper API."""
from __future__ import annotations

from untappd_scraper.beer import Beer

beer_ids = [4266838, 4266841]

for beer_id in beer_ids:
    beer = Beer(beer_id)
    print(f"\n{beer.name=} {beer.brewery=}\t{beer.global_rating=}")
