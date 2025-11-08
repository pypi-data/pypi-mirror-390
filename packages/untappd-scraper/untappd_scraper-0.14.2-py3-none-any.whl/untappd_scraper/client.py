"""Handle httpx client and hishel caching."""

import logging
import os
from datetime import timedelta
from typing import Final

import hishel
import logfire

CACHE: Final = timedelta(minutes=5).total_seconds()
TIMEOUT: Final = timedelta(seconds=20).total_seconds()


logging.getLogger("hishel.controller").setLevel(logging.INFO)
logging.getLogger("httpcore").setLevel(logging.INFO)


def get_httpx_client() -> hishel.CacheClient:
    """Return a cachhed HTTPX client with caching enabled."""
    storage = hishel.FileStorage(ttl=CACHE)
    controller = hishel.Controller(force_cache=True)
    return hishel.CacheClient(
        follow_redirects=True,
        storage=storage,
        controller=controller,
        timeout=TIMEOUT,
        # Untappd / Cloudflare issues a JavaScript challenge for http1 requests only, perhaps
        http1=False,
        http2=True,
    )


client = get_httpx_client()


if os.getenv("LOGFIRE_TOKEN"):
    logfire.instrument_httpx(client)
