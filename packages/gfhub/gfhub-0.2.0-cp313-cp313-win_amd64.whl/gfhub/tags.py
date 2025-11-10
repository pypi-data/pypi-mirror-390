"""Utilities for working with tags."""

from __future__ import annotations

from typing import Any

import yaml


def parse_dict(tags: list[str]) -> dict[str, Any]:
    """Parse a list of tags into a dictionary."""
    ret = {}
    for tag in tags:
        ret[parse_name(tag)] = parse_value(tag)
    return ret


def parse_value(tag: str) -> Any:
    """Parse the value from a tag."""
    _, *values = tag.split(":", 1)
    if not values:
        return None
    value = values[0]
    if "," in value:
        value = tuple(yaml.safe_load(f"key: [{value}]")["key"])
    else:
        value = yaml.safe_load(f"key: {value}")["key"]
    return value


def parse_name(tag: str) -> Any:
    """Parse the name from a tag."""
    name, *_ = tag.split(":", 1)
    return name
