from typing import Iterable, TypeVar

T = TypeVar("T")


def get_unique_item_if_exists(iterable: Iterable[T], name: str | None = None) -> T | None:
    """Get the unique item from the collection, if any element exists inside the collection.

    Raises a ValueError if there are multiple unique elements. Returns None if the collection is empty.
    """
    item = ...
    in_name = f" in `{name}`" if name is not None else ""
    for x in iterable:
        if item is ...:
            item = x
        if x != item:
            raise ValueError(f"Multiple values{in_name} are not permitted. Found {x}, {item}")
    if item is ...:
        return None
    return item


def get_unique_item(collection: Iterable[T], name: str | None = None) -> T:
    """Get the unique item from the collection, ignoring equal duplicates.

    Raises a ValueError if there is not a single, unique element."""
    unique_item_or_none = get_unique_item_if_exists(collection, name)
    if unique_item_or_none is None:
        in_name = f" in `{name}`" if name is not None else ""
        raise ValueError(f"There should be at least one item{in_name}")
    return unique_item_or_none
