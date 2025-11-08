from __future__ import annotations

from typing import Any
from typing_extensions import override

from ._proxy import LazyProxy


class ResourcesProxy(LazyProxy[Any]):
    """A proxy for the `commerce_shopper_search.resources` module.

    This is used so that we can lazily import `commerce_shopper_search.resources` only when
    needed *and* so that users can just import `commerce_shopper_search` and reference `commerce_shopper_search.resources`
    """

    @override
    def __load__(self) -> Any:
        import importlib

        mod = importlib.import_module("commerce_shopper_search.resources")
        return mod


resources = ResourcesProxy().__as_proxied__()
