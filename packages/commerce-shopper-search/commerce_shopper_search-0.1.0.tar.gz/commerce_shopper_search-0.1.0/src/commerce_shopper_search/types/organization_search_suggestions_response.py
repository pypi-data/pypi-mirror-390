# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel
from .suggestion import Suggestion
from .suggested_phrase import SuggestedPhrase

__all__ = ["OrganizationSearchSuggestionsResponse", "EinsteinSuggestedPhrases"]


class EinsteinSuggestedPhrases(BaseModel):
    popular_search_phrases: Optional[List[SuggestedPhrase]] = FieldInfo(alias="popularSearchPhrases", default=None)
    """A list of popular search phrases suggested by Einstein. This list can be empty."""

    recent_search_phrases: Optional[List[SuggestedPhrase]] = FieldInfo(alias="recentSearchPhrases", default=None)
    """A list of recent search phrases suggested by Einstein. This list can be empty."""


class OrganizationSearchSuggestionsResponse(BaseModel):
    search_phrase: str = FieldInfo(alias="searchPhrase")
    """The query phrase (q) for which suggestions where made."""

    brand_suggestions: Optional[Suggestion] = FieldInfo(alias="brandSuggestions", default=None)
    """Document representing a suggestion."""

    category_suggestions: Optional[Suggestion] = FieldInfo(alias="categorySuggestions", default=None)
    """Document representing a suggestion."""

    custom_suggestion: Optional[Suggestion] = FieldInfo(alias="customSuggestion", default=None)
    """Document representing a suggestion."""

    einstein_suggested_phrases: Optional[EinsteinSuggestedPhrases] = FieldInfo(
        alias="einsteinSuggestedPhrases", default=None
    )
    """Einstein-suggested phrases containing popular and recent search phrases."""

    product_suggestions: Optional[Suggestion] = FieldInfo(alias="productSuggestions", default=None)
    """Document representing a suggestion."""
