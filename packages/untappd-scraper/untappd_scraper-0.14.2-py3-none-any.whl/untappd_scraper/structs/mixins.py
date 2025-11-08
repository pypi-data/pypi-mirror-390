"""Mixin classes."""
from __future__ import annotations

from typing import Protocol


class HasBeerId(Protocol):
    """Check a class has a beer id."""

    beer_id: int


class HasVenueId(Protocol):
    """Check a class has a venue id."""

    venue_id: int


class IdStrMixin:
    """Provide string versions of integer IDs."""

    @property
    def beer_id_str(self: HasBeerId) -> str:
        """Return str version of Beer ID.

        JSON keys are str but dict can be int. Can get dupe JSON keys.

        Returns:
            str: string version of beer ID
        """
        return str(self.beer_id)

    @property
    def venue_id_str(self: HasVenueId) -> str:
        """Return str version of Venue ID.

        JSON keys are str but dict can be int. Can get dupe JSON keys.

        Returns:
            str: string version of venue ID
        """
        return str(self.venue_id)


class HasBeerDetails(Protocol):
    """Check if a class has beer details."""

    name: str
    brewery: str
    style: str
    global_rating: float


class BeerStrMixin:
    """Provide a nice description of a beer."""

    def __str__(self: HasBeerDetails) -> str:
        """Create a summary description of a beer.

        Returns:
            str: beer description
        """
        return f"{self.name} by {self.brewery}, {self.style} ({self.global_rating})"
