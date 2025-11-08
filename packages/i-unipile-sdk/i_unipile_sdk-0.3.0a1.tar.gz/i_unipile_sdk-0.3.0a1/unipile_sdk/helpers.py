"""
Utility functions
"""

from typing import Any, AsyncGenerator, Awaitable, Callable, Dict, Generator, List
from urllib.parse import urlparse
from uuid import UUID


def pick(base: Dict[Any, Any], *keys: str) -> Dict[Any, Any]:
    """Return a dict composed of key value pairs for keys passed as args."""
    result = {}
    for key in keys:
        if key not in base:
            continue
        value = base.get(key)
        if value is None and key == "cursor":
            continue
        result[key] = value
    return result


def iterate_paginated_api(
    function: Callable[..., Any], **kwargs: Any
) -> Generator[Any, None, None]:
    """Return an iterator over the results of any paginated Unipile API."""
    next_cursor = kwargs.pop("cursor", None)
    max_total = kwargs.pop("max_total", 100)
    items_found = 0

    while True:
        # TODO: add random delays?
        response = function(**kwargs, cursor=next_cursor)

        # WARN: use pydantic mode here, when we convert search resuts to
        # pydantic model cusor/items
        next_cursor = response.cursor

        items_found += len(response.items)
        for result in response.items:
            yield result

        if items_found >= max_total or not next_cursor:
            break


def collect_paginated_api(function: Callable[..., Any], **kwargs: Any) -> List[Any]:
    """Collect all the results of paginating an API into a list."""
    return [result for result in iterate_paginated_api(function, **kwargs)]


async def async_iterate_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> AsyncGenerator[Any, None]:
    """Return an async iterator over the results of any paginated Unipile API."""
    next_cursor = kwargs.pop("cursor", None)

    while True:
        response = await function(**kwargs, cursor=next_cursor)
        for result in response.get("results"):
            yield result

        next_cursor = response.get("cursor")
        if next_cursor is None:
            return


async def async_collect_paginated_api(
    function: Callable[..., Awaitable[Any]], **kwargs: Any
) -> List[Any]:
    """Collect asynchronously all the results of paginating an API into a list."""
    return [result async for result in async_iterate_paginated_api(function, **kwargs)]


def is_full_block(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full block."""
    return response.get("object") == "block" and "type" in response


def is_full_page(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full page."""
    return response.get("object") == "page" and "url" in response


def is_full_database(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full database."""
    return response.get("object") == "database" and "title" in response


def is_full_page_or_database(response: Dict[Any, Any]) -> bool:
    """Return `True` if `response` is a full database or a full page."""
    if response.get("object") == "database":
        return is_full_database(response)
    return is_full_page(response)


def is_full_user(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full user."""
    return "type" in response


def is_full_comment(response: Dict[Any, Any]) -> bool:
    """Return `True` if response is a full comment."""
    return "type" in response


def is_text_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is a text."""
    return rich_text.get("type") == "text"


def is_equation_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is an equation."""
    return rich_text.get("type") == "equation"


def is_mention_rich_text_item_response(rich_text: Dict[Any, Any]) -> bool:
    """Return `True` if `rich_text` is a mention."""
    return rich_text.get("type") == "mention"

def reminds_url(input: str) -> bool:
    """
    >>> reminds_url('yandex.ru.com/somepath')
    True
    """
    if "/" not in input:
        return False

    ltext = input.lower().split("/")[0]
    return ltext.startswith(("http", "www", "ftp"))
