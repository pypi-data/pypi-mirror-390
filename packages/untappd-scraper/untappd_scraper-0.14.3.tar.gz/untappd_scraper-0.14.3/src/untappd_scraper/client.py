"""Handle httpx client and hishel caching."""

import logging
import os
from datetime import timedelta
from typing import Final

import logfire
from hishel import CacheOptions, SpecificationPolicy, SyncSqliteStorage
from hishel.httpx import SyncCacheClient

CACHE: Final = timedelta(minutes=5).total_seconds()
TIMEOUT: Final = timedelta(seconds=20).total_seconds()


logging.getLogger("httpcore").setLevel(logging.INFO)


def get_httpx_client() -> SyncCacheClient:
    """Return an HTTPX client with caching enabled."""
    storage = SyncSqliteStorage(default_ttl=CACHE)
    policy = SpecificationPolicy(cache_options=CacheOptions(allow_stale=True))
    return SyncCacheClient(
        follow_redirects=True,
        storage=storage,
        policy=policy,
        timeout=TIMEOUT,
        # Untappd / Cloudflare issues a JavaScript challenge for http1 requests only, perhaps
        http1=False,
        http2=True,
    )


client = get_httpx_client()


if os.getenv("LOGFIRE_TOKEN"):
    logfire.instrument_httpx(client)
