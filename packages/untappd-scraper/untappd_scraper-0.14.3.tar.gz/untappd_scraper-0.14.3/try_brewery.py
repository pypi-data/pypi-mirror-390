"""Set up expectations for untappd-scraper API."""

from __future__ import annotations

from untappd_scraper.brewery import Brewery
from untappd_scraper.logging_config import configure_logging

logger = configure_logging(__name__)


brewery = Brewery.from_name("big niles")

print(brewery)  # noqa: T201
