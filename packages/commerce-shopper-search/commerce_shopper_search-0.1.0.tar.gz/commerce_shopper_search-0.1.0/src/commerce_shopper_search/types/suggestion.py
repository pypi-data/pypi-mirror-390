# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .suggested_terms import SuggestedTerms
from .suggested_phrase import SuggestedPhrase

__all__ = ["Suggestion"]


class Suggestion(BaseModel):
    suggested_terms: List[SuggestedTerms] = FieldInfo(alias="suggestedTerms")
    """A list of suggested terms. This list can be empty."""

    suggested_phrases: Optional[List[SuggestedPhrase]] = FieldInfo(alias="suggestedPhrases", default=None)
    """A list of suggested phrases. This list can be empty."""

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
    else:
        __pydantic_extra__: Dict[str, object]
