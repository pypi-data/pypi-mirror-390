"""General utilities for processing user lists."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from dateutil.parser import parse as parse_date

if TYPE_CHECKING:  # pragma: no cover
    from datetime import date

    from requests_html import Element


@dataclass
class WebUserListBeerDetails:
    """Optional details a list beer can have."""

    beer_notes: str | None = None
    quantity: int | None = None
    serving: str | None = None
    purchased_date: date | None = None
    purchased_at: str | None = None
    purchase_price: float | None = None
    bottled_date: date | None = None
    best_by_date: date | None = None


def parse_more_details(more_info_el: Element) -> WebUserListBeerDetails:
    """Parse any info from "show details" in a list beer.

    Args:
        more_info_el (Element): section for a beer for more details

    Raises:
        ValueError: unknown list label

    Returns:
        WebUserListBeerDetails: optional extra details in list
    """
    if not more_info_el:
        return WebUserListBeerDetails()  # pragma: no cover

    label_dispatch = {
        "Notes": ("beer_notes", parse_more_details_str),
        "Quantity": ("quantity", parse_more_details_int),
        "Serving Style": ("serving", parse_more_details_str),
        "Purchase Date": ("purchased_date", parse_more_details_date),
        "Purchase Location": ("purchased_at", parse_more_details_str),
        "Purchase Price": ("purchase_price", parse_more_details_float),
        "Bottled Date": ("bottled_date", parse_more_details_date),
        "Best By Date": ("best_by_date", parse_more_details_date),
    }

    more_details = WebUserListBeerDetails()

    for more_info in more_info_el.find("li"):
        label: str = more_info.find("label", first=True).text
        label_value: Element = more_info.find("p", first=True)

        attr, func = label_dispatch.get(label, (None, None))
        if attr and func:
            setattr(more_details, attr, func(label_value))
        else:  # pragma: no cover
            msg = f"don't understand label {label} {more_info_el.html=}"
            raise ValueError(msg)

    return more_details


def parse_more_details_str(label_value: Element) -> str:
    """Parse a string label value from more-details.

    Args:
        label_value (Element): label's value

    Returns:
        str: text value of element
    """
    return label_value.text


def parse_more_details_int(label_value: Element) -> int:
    """Parse a integer label value from more-details.

    Args:
        label_value (Element): label's value

    Returns:
        int: integer value of element
    """
    return int(label_value.text)


def parse_more_details_float(label_value: Element) -> float:
    """Parse a decinal label value from more-details.

    Args:
        label_value (Element): label's value

    Returns:
        float: decimal value of element
    """
    return float(label_value.text)


def parse_more_details_date(label_value: Element) -> date:
    """Parse a date label value from more-details.

    Args:
        label_value (Element): label's value

    Returns:
        date: date value of element
    """
    return parse_date(label_value.attrs["data-date"]).date()
