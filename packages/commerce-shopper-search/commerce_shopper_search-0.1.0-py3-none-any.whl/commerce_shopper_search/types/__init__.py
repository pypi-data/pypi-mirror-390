# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from . import product_search_refinement_value, organization_product_search_response
from .. import _compat
from .image import Image as Image
from .suggestion import Suggestion as Suggestion
from .product_ref import ProductRef as ProductRef
from .currency_code import CurrencyCode as CurrencyCode
from .suggested_terms import SuggestedTerms as SuggestedTerms
from .suggested_phrase import SuggestedPhrase as SuggestedPhrase
from .product_promotion import ProductPromotion as ProductPromotion
from .currency_code_param import CurrencyCodeParam as CurrencyCodeParam
from .product_price_table import ProductPriceTable as ProductPriceTable
from .variation_attribute import VariationAttribute as VariationAttribute
from .product_search_refinement_value import ProductSearchRefinementValue as ProductSearchRefinementValue
from .organization_product_search_params import OrganizationProductSearchParams as OrganizationProductSearchParams
from .organization_product_search_response import OrganizationProductSearchResponse as OrganizationProductSearchResponse
from .organization_search_suggestions_params import (
    OrganizationSearchSuggestionsParams as OrganizationSearchSuggestionsParams,
)
from .organization_search_suggestions_response import (
    OrganizationSearchSuggestionsResponse as OrganizationSearchSuggestionsResponse,
)

# Rebuild cyclical models only after all modules are imported.
# This ensures that, when building the deferred (due to cyclical references) model schema,
# Pydantic can resolve the necessary references.
# See: https://github.com/pydantic/pydantic/issues/11250 for more context.
if _compat.PYDANTIC_V1:
    product_search_refinement_value.ProductSearchRefinementValue.update_forward_refs()  # type: ignore
    organization_product_search_response.OrganizationProductSearchResponse.update_forward_refs()  # type: ignore
else:
    product_search_refinement_value.ProductSearchRefinementValue.model_rebuild(_parent_namespace_depth=0)
    organization_product_search_response.OrganizationProductSearchResponse.model_rebuild(_parent_namespace_depth=0)
