"""Test out type hints for Pydantic."""  # noqa: INP001

from typing import reveal_type

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


@dataclass
class Plain:
    """No special dataclass freezing."""

    x: int = 1


@dataclass(frozen=True)
class Frozen:
    """Frozen dataclass."""

    x: int = 1


@dataclass(config=ConfigDict(frozen=True))
class ConfigFrozen:
    """Frozen dataclass via config."""

    x: int = 1


@dataclass(frozen=False)
class FrozenFalse:
    """Explicitly not frozen dataclass."""

    x: int = 1


a = Plain()
reveal_type(a.x)

b = Frozen()
reveal_type(b.x)

c = ConfigFrozen()
reveal_type(c.x)

d = FrozenFalse()
reveal_type(d.x)
