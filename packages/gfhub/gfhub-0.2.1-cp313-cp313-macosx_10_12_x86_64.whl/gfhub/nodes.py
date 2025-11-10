"""Helper functions for creating pipeline nodes."""

from typing import Any


def on_file_upload(
    name: str = "on_file_upload", /, *, tags: list[str] | None = None
) -> dict:
    """Create an 'on_file_upload' trigger node.

    Args:
        name: The name of the node
        tags: Optional list of tags to filter files (format: "tag_name" or "tag_name:value")

    Returns:
        A node dictionary in JsonNode format
    """
    config = {}
    if tags:
        config["tags"] = tags

    return {
        "name": name,
        "type": "on_file_upload",
        "config": config,
    }


def on_manual_trigger(name: str = "on_manual_trigger", /) -> dict:
    """Create an 'on_manual_trigger' trigger node.

    Args:
        name: The name of the node

    Returns:
        A node dictionary in JsonNode format
    """
    return {
        "name": name,
        "type": "on_manual_trigger",
        "config": {},
    }


def load(name: str = "load", /) -> dict:
    """Create a 'load' node that loads a file from storage.

    Args:
        name: The name of the node

    Returns:
        A node dictionary in JsonNode format
    """
    return {
        "name": name,
        "type": "load",
        "config": {},
    }


def load_tags(name: str = "load_tags", /) -> dict:
    """Create a 'load_tags' node that loads file tags.

    Args:
        name: The name of the node

    Returns:
        A node dictionary in JsonNode format
    """
    return {
        "name": name,
        "type": "load_tags",
        "config": {},
    }


def function(name: str = "", /, *, function: str, kwargs: dict[str, Any]) -> dict:
    """Create a 'function' node that executes a custom function.

    Args:
        name: The name of the node
        function: The name of the function to execute
        kwargs: Keyword arguments to pass to the function

    Returns:
        A node dictionary in JsonNode format
    """
    if not name:
        name = function

    return {
        "name": name,
        "type": "function",
        "config": {
            "function": function,
            "kwargs": kwargs,
        },
    }


def save(name: str = "save", /, *, tags: list[str] | None = None) -> dict:
    """Create a 'save' node that saves files to storage.

    Args:
        name: The name of the node
        tags: Optional list of tags to associate with saved files (format: "tag_name" or "tag_name:value")

    Returns:
        A node dictionary in JsonNode format
    """
    config = {}
    if tags:
        config["tags"] = tags

    return {
        "name": name,
        "type": "save",
        "config": config,
    }


def concat(name: str = "concat", /) -> dict:
    """Create a 'concat' node that concatenates multiple inputs.

    Args:
        name: The name of the node

    Returns:
        A node dictionary in JsonNode format
    """
    return {
        "name": name,
        "type": "concat",
        "config": {},
    }


def merge(name: str = "merge", /) -> dict:
    """Create a 'merge' node that merges multiple inputs.

    Args:
        name: The name of the node

    Returns:
        A node dictionary in JsonNode format
    """
    return {
        "name": name,
        "type": "merge",
        "config": {},
    }


def filter_files(name: str = "filter_files", /, *, tags: list[str]) -> dict:
    """Create a 'filter_files' node that filters files by tags.

    Args:
        name: The name of the node
        tags: List of tags to filter files (format: "tag_name" or "tag_name:value")

    Returns:
        A node dictionary in JsonNode format
    """
    return {
        "name": name,
        "type": "filter_files",
        "config": {
            "tags": tags,
        },
    }
