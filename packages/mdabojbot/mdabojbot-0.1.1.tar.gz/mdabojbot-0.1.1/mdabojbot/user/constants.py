from enum import StrEnum, auto


class UserGroup(StrEnum):
    """Users group."""

    ADMIN = auto()
    REGULAR = auto()
