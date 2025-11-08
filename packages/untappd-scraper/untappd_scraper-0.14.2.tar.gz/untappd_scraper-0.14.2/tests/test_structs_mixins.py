"""Test the `untappd_scraper` mixin utilities."""

from __future__ import annotations

from untappd_scraper.structs.mixins import BeerStrMixin, IdStrMixin


def test_id_str_mixin() -> None:
    """Test the ID string mixin."""

    class TestClass(IdStrMixin):
        def __init__(self, beer_id: int, venue_id: int) -> None:
            self.beer_id = beer_id
            self.venue_id = venue_id

    result = TestClass(123, 456)

    assert result.beer_id_str == "123"
    assert result.venue_id_str == "456"


def test_beer_str_mixin() -> None:
    """Test the beer string mixin."""

    class TestClass(BeerStrMixin):
        def __init__(self, name: str, brewery: str, style: str, rating: float) -> None:
            self.name = name
            self.brewery = brewery
            self.style = style
            self.global_rating = rating

    result = TestClass("Beer Name", "Brewery Name", "IPA", 4.5)

    assert str(result) == "Beer Name by Brewery Name, IPA (4.5)"
