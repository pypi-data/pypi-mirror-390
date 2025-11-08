# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["SuggestedTerms", "Term"]


class Term(BaseModel):
    completed: bool
    """Returns whether this term value is a completion match."""

    corrected: bool
    """Returns whether this term value is a correction match."""

    exact_match: bool = FieldInfo(alias="exactMatch")
    """Returns whether this term value is a exact match."""

    value: str
    """Returns the term value."""


class SuggestedTerms(BaseModel):
    original_term: str = FieldInfo(alias="originalTerm")
    """Returns the original term that the suggested terms relates to."""

    terms: Optional[List[Term]] = None
    """Returns the suggested terms."""
