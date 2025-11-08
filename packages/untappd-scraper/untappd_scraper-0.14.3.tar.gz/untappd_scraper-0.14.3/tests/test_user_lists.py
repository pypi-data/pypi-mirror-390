"""Test User List functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from untappd_scraper.user_lists import (
    WebUserList,
    WebUserListBeer,
    extract_list_beers,
    load_user_lists,
    page_sort_orders,
)

if TYPE_CHECKING:  # pragma: no cover
    from requests_html import HTML


def test_page_sort_orders_userlist(fridge_list_html: HTML) -> None:
    result = page_sort_orders(fridge_list_html)  # pyright: ignore[reportArgumentType]

    assert len(result) >= 12
    assert "date_asc" in result
    assert "style_name_desc" in result


def test_page_sort_orders_restricted_userlist(fridge_list_html: HTML) -> None:
    result = page_sort_orders(fridge_list_html, useful_sorts_keys={"date"})  # pyright: ignore[reportArgumentType]]

    assert len(result) == 1
    assert "date" in result


def test_page_sort_orders_wishlist(wishlist_html: HTML) -> None:
    result = page_sort_orders(wishlist_html)  # pyright: ignore[reportArgumentType]

    assert len(result) >= 10
    assert "date_asc" in result
    assert "style_name_desc" not in result


# ----- Higher level tests faking the html fetch -----


@pytest.fixture
def sample_list(_mock_user_lists_get: None) -> WebUserList:
    lists = load_user_lists("test")
    assert len(lists) == 13

    return lists[1]


def test_load_user_lists(sample_list: WebUserList) -> None:
    result = sample_list

    assert result.name == "My Fridge"
    assert result.num_items
    assert result.is_wishlist is False
    assert result.full_scrape is False


# @pytest.mark.usefixtures('_mock_fridge_list_get')
def test_extract_list_beers(fridge_list_resp: MockResponse) -> None:
    result = tuple(extract_list_beers(fridge_list_resp))

    assert result
    assert isinstance(result[0], WebUserListBeer)
    assert result[0].beer_id
