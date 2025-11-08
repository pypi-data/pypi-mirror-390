"""HTML session to be shared across all modules."""

from __future__ import annotations

import logging
import time
from datetime import timedelta
from typing import TYPE_CHECKING, Any, Final

import ratelim
import requests
from requests_cache import AnyResponse, CacheMixin
from requests_html import HTMLResponse, HTMLSession
from tenacity import RetryCallState, _utils, retry_base
from tenacity.wait import wait_base

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Callable

logger = logging.getLogger(__name__)

CACHE_EXPIRY: Final = timedelta(minutes=5)
MAX_GET_MIN1: Final = 40  # max number of web GETs in a minute
MAX_RETRY_ATTEMPTS: Final = 9  # give up after this many retries
MAX_RETRY_SECS: Final = 180  # never wait more than this for a retry
MIN1: Final = 60  # seconds
TIMEOUT_CONNECT: Final = 5.0
TIMEOUT_READ: Final = 15.0

# Allow user to check these. Don't raise an exception here
ACCEPTABLE_HTTP_STATUS: Final[frozenset[int]] = frozenset((requests.codes["not_found"],))


class CachedHTMLSession(CacheMixin, HTMLSession):  # pyright: ignore[reportIncompatibleMethodOverride]
    """Session with features from both CachedSession and HTMLSession."""


_html_session = CachedHTMLSession(cache_name="html", expire_after=CACHE_EXPIRY)


@ratelim.greedy(MAX_GET_MIN1, MIN1)
def get(url: str, *, emulate_404: bool = False, **kwargs: Any) -> HTMLResponse:  # noqa: ANN401
    """Get a URL.

    Handles too many requests errors, and retries after waiting

    Args:
        url (str): URL to get
        emulate_404 (bool): if True, return a 404 response
        kwargs (dict): extra requests options, eg, params and headers

    Returns:
        requests.Response: response to get
    """
    if emulate_404:
        url = "https://httpbin.org/status/404"

    return _get(url, **kwargs)


# ----- Tenacity -----


class RetryAfter(wait_base):
    """Strategy that tries to wait as per Retry-After header.

    Tries to wait for the length specified by the Retry-After header,
    or the underlying wait / fallback strategy if not.
    See RFC 6585 § 4.
    """

    def __init__(self, fallback: wait_base) -> None:
        """Store fallback strategy in case we can't work out retry wait time.

        Args:
            fallback (wait_base): fallback wait strategy if no Retry-After found
        """
        self.fallback = fallback

    def __call__(self, retry_state: RetryCallState) -> int:  # pragma: no cover
        """Return seconds to wait until retry.

        Args:
            retry_state (RetryState): State of retry, with .outcome property
                storing exception.

        Returns:
            int: seconds to wait
        """
        assert retry_state.outcome
        exc = retry_state.outcome.exception()
        if isinstance(exc, requests.HTTPError):
            retry_after = exc.response.headers.get("Retry-After")
            logger.debug("Searching response header and found Retry-After of %s", retry_after)

            try:
                return int(retry_after)  # pyright: ignore[reportArgumentType]
            except (TypeError, ValueError):
                return int(self.fallback(retry_state))

        return int(self.fallback(retry_state))


def my_before_sleep_log(
    user_logger: logging.Logger, *, exc_info: bool = False
) -> Callable[[RetryCallState], None]:
    """Before call strategy that logs to some logger the attempt.

    Logging level is determined by the number of retries.

    Lifted from Tenacity function and removed hard-coded log level

    Args:
        user_logger (Logger): logger to use
        exc_info (bool, optional): Is there an exception. Defaults to False.

    Returns:
        logging function
    """

    def log_it(retry_state: RetryCallState) -> None:  # pragma: no cover
        if retry_state.attempt_number < 1:
            log_level = logging.DEBUG
        elif retry_state.attempt_number == 1:
            log_level = logging.INFO
        else:
            log_level = logging.WARNING

        assert retry_state.outcome

        if retry_state.outcome.failed:
            ex = retry_state.outcome.exception()
            verb, retry_value = "raised", f"{type(ex).__name__}: {ex}"

            if exc_info and retry_state.outcome:
                local_exc_info = retry_state.outcome.exception()
            else:
                local_exc_info = False
        else:
            verb, retry_value = "returned", retry_state.outcome.result()
            local_exc_info = False  # exc_info does not apply when no exception

        user_logger.log(
            log_level,
            "Retrying %s (%s attempt) in %s seconds as it %s %s.",
            _utils.get_callback_name(retry_state.fn),  # pyright: ignore[reportArgumentType]
            _utils.to_ordinal(retry_state.attempt_number),
            retry_state.next_action.sleep,  # pyright: ignore[reportOptionalMemberAccess]
            verb,
            retry_value,
            exc_info=local_exc_info,
        )

    return log_it


def is_throttling_related_exception(excp: Exception) -> bool:  # pragma: no cover
    """Check is the exception is a requests one and throttling related.

    Args:
        excp (Exception): exception raised

    Returns:
        bool: was it a throttle
    """
    return (
        isinstance(excp, requests.HTTPError)
        and excp.response.status_code == requests.codes.too_many_requests
    )


class RetryIfThrottling(retry_base):
    """Retry class which only retries if a throttling exception occured.

    From https://www.seelk.co/blog/efficient-client-side-handling-of-api-throttling-in-python-with-tenacity/
    """

    def __call__(self, retry_state: RetryCallState) -> bool:  # pragma: no cover
        """Return if the call raised an exception and it's a throttle.

        Args:
            retry_state (RetryCallState): info about current retry invocation

        Returns:
            bool: is it throttling related
        """
        if (
            retry_state.outcome
            and retry_state.outcome.failed
            and (exception := retry_state.outcome.exception())
        ):
            return is_throttling_related_exception(exception)  # pyright: ignore[reportArgumentType]
        return False


# ---- Main part of tenacity retry ----

# Retry too-many-requests after a delay

# - Retries if throttle response received
# - Checks for Retry-After header and wait that long
# - If no header, waits expontially longer each retry
# - logs retries, with increasing severity as attempts increase


def _get(url: str, **kwargs: Any) -> HTMLResponse:  # noqa: ANN401
    resp: AnyResponse | None = None
    last_exc: Exception | None = None

    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            resp = _html_session.get(url, timeout=(TIMEOUT_CONNECT, TIMEOUT_READ), **kwargs)
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exc = e
            logger.debug("Connection error on attempt %d: %s", attempt, last_exc)
            time.sleep(5)
        else:
            break
    else:
        if last_exc:
            logger.error(
                "Giving up after %d attempts due to connection errors.", MAX_RETRY_ATTEMPTS
            )
            raise last_exc

        logger.error("Giving up after %d attempts.", MAX_RETRY_ATTEMPTS)
        msg = f"Failed to get a valid response after {MAX_RETRY_ATTEMPTS} retries."
        raise RuntimeError(msg)

    logger.debug(
        "GET %s (%s) received %s\tExpires: %s, Headers: %s",
        url,
        kwargs,
        resp,
        resp.expires,
        resp.headers,
    )

    if resp.status_code not in ACCEPTABLE_HTTP_STATUS:
        resp.raise_for_status()  # pragma: no cover

    return resp  # pyright: ignore[reportReturnType]
