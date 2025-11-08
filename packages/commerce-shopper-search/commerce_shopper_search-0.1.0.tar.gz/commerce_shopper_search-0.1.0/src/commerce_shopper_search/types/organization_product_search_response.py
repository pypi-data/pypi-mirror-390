# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from .image import Image
from .._models import BaseModel
from .suggestion import Suggestion
from .product_ref import ProductRef
from .currency_code import CurrencyCode
from .product_promotion import ProductPromotion
from .product_price_table import ProductPriceTable
from .variation_attribute import VariationAttribute

__all__ = [
    "OrganizationProductSearchResponse",
    "Hit",
    "HitImageGroup",
    "HitPriceRange",
    "HitProductType",
    "HitVariant",
    "HitVariationGroup",
    "Refinement",
    "SortingOption",
    "PageMetaTag",
]


class HitImageGroup(BaseModel):
    images: List[Image]
    """The images of the image group."""

    view_type: str = FieldInfo(alias="viewType")
    """
    The String256 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 256 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      128 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 85 characters.
    """

    variation_attributes: Optional[List[VariationAttribute]] = FieldInfo(alias="variationAttributes", default=None)
    """Returns a list of variation attributes applying to this image group."""


class HitPriceRange(BaseModel):
    max_price: Optional[float] = FieldInfo(alias="maxPrice", default=None)
    """
    Maximum price for the given pricebook (usually for a master Product would be the
    price for the Variant which has the highest price out of all Variants in that
    pricebook)
    """

    min_price: Optional[float] = FieldInfo(alias="minPrice", default=None)
    """
    Minimum price for the given pricebook (usually for a master Product would be the
    price for the Variant which has the least price out of all Variants in that
    pricebook)
    """

    pricebook: Optional[str] = None
    """
    The String256 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 256 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      128 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 85 characters.
    """


class HitProductType(BaseModel):
    bundle: Optional[bool] = None
    """A flag indicating whether the product is a bundle."""

    item: Optional[bool] = None
    """A flag indicating whether the product is a standard item."""

    master: Optional[bool] = None
    """A flag indicating whether the product is a master."""

    option: Optional[bool] = None
    """A flag indicating whether the product is an option."""

    set: Optional[bool] = None
    """A flag indicating whether the product is a set."""

    variant: Optional[bool] = None
    """A flag indicating whether the product is a variant."""

    variation_group: Optional[bool] = FieldInfo(alias="variationGroup", default=None)
    """A flag indicating whether the product is a variation group."""


class HitVariant(BaseModel):
    product_id: str = FieldInfo(alias="productId")
    """The ID (SKU) of the variant."""

    orderable: Optional[bool] = None
    """A flag indicating whether the variant is orderable."""

    price: Optional[float] = None
    """The sales price of the variant."""

    product_promotions: Optional[List[ProductPromotion]] = FieldInfo(alias="productPromotions", default=None)
    """The array of active customer product promotions for this product.

    This array can be empty. Coupon promotions are not returned in this array.
    """

    tiered_prices: Optional[List[ProductPriceTable]] = FieldInfo(alias="tieredPrices", default=None)
    """List of tiered prices if the product is a variant"""

    variation_values: Optional[Dict[str, str]] = FieldInfo(alias="variationValues", default=None)
    """The actual variation attribute ID - value pairs."""


class HitVariationGroup(BaseModel):
    orderable: bool
    """A flag indicating whether the variation group is orderable."""

    price: float
    """The sales price of the variation group."""

    product_id: str = FieldInfo(alias="productId")
    """The ID (SKU) of the variation group."""

    variation_values: Dict[str, str] = FieldInfo(alias="variationValues")
    """The actual variation attribute ID - value pairs."""


class Hit(BaseModel):
    product_id: str = FieldInfo(alias="productId")
    """The ID (SKU) of the product."""

    currency: Optional[CurrencyCode] = None
    """
    A three letter uppercase currency code conforming to the
    [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
    string `N/A` indicating that a currency is not applicable.
    """

    hit_type: Optional[str] = FieldInfo(alias="hitType", default=None)
    """
    The String256 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 256 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      128 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 85 characters.
    """

    image: Optional[Image] = None
    """The first image of the product hit for the configured viewtype."""

    image_groups: Optional[List[HitImageGroup]] = FieldInfo(alias="imageGroups", default=None)
    """The array of product image groups."""

    orderable: Optional[bool] = None
    """A flag indicating whether the product is orderable."""

    price: Optional[float] = None
    """The sales price of the product.

    In complex products, like master or set, this is the minimum price of related
    child products.
    """

    price_max: Optional[float] = FieldInfo(alias="priceMax", default=None)
    """
    The maximum sales of related child products in complex products like master or
    set.
    """

    price_ranges: Optional[List[HitPriceRange]] = FieldInfo(alias="priceRanges", default=None)
    """
    Array of one or more price range objects representing one or more Pricebooks in
    context for the site.
    """

    product_name: Optional[str] = FieldInfo(alias="productName", default=None)
    """
    The String4000 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 4000 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 4000
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      2000 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 1333 characters.
    """

    product_promotions: Optional[List[ProductPromotion]] = FieldInfo(alias="productPromotions", default=None)
    """The array of active customer product promotions for this product.

    This array can be empty. Coupon promotions are not returned in this array.
    """

    product_type: Optional[HitProductType] = FieldInfo(alias="productType", default=None)
    """Document representing a product type."""

    represented_product: Optional[ProductRef] = FieldInfo(alias="representedProduct", default=None)
    """Document representing a product reference."""

    represented_products: Optional[List[ProductRef]] = FieldInfo(alias="representedProducts", default=None)
    """All the represented products."""

    tiered_prices: Optional[List[ProductPriceTable]] = FieldInfo(alias="tieredPrices", default=None)
    """The document represents list of tiered prices if the product is a variant"""

    variants: Optional[List[HitVariant]] = None
    """The array of actual variants.

    Only for master, variation group, and variant types. This array can be empty.
    """

    variation_attributes: Optional[List[VariationAttribute]] = FieldInfo(alias="variationAttributes", default=None)
    """The array of represented variation attributes, for the master product only.

    This array can be empty.
    """

    variation_groups: Optional[List[HitVariationGroup]] = FieldInfo(alias="variationGroups", default=None)
    """The array of actual variation groups.

    Only for master, variation group, and variant types. This array can be empty.
    """

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


class Refinement(BaseModel):
    attribute_id: str = FieldInfo(alias="attributeId")
    """
    The String256 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 256 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      128 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 85 characters.
    """

    label: Optional[str] = None
    """
    The String256 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 256 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      128 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 85 characters.
    """

    values: Optional[List["ProductSearchRefinementValue"]] = None
    """The sorted array of refinement values. This array can be empty."""


class SortingOption(BaseModel):
    id: str
    """
    The String256 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 256 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      128 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 85 characters.
    """

    label: str
    """
    The String4000 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 4000 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 4000
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      2000 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 1333 characters.
    """


class PageMetaTag(BaseModel):
    id: Optional[str] = None
    """
    The String256 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 256 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      128 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 85 characters.
    """

    value: Optional[str] = None
    """
    Locale-specific value of the Page Meta Tag, evaluated by resolving the rule set
    for the given Business Manager ID.
    """


class OrganizationProductSearchResponse(BaseModel):
    hits: List[Hit]
    """A sorted array of search hits (`ProductSearchHit` objects).

    The array can be empty.
    """

    limit: int
    """Maximum records to retrieve per request, not to exceed the maximum defined.

    A limit must be at least 1 so at least one record is returned (if any match the
    criteria).
    """

    query: str
    """The query string that was searched for."""

    refinements: List[Refinement]
    """The sorted array of search refinements. This array can be empty."""

    search_phrase_suggestions: Suggestion = FieldInfo(alias="searchPhraseSuggestions")
    """Document representing a suggestion."""

    sorting_options: List[SortingOption] = FieldInfo(alias="sortingOptions")
    """The sorted array of search sorting options. This array can be empty."""

    total: int
    """The total number of hits that match the search's criteria.

    This can be greater than the number of results returned as search results are
    pagenated.
    """

    page_meta_tags: Optional[List[PageMetaTag]] = FieldInfo(alias="pageMetaTags", default=None)
    """Page Meta tags associated with the search result."""

    selected_refinements: Optional[Dict[str, str]] = FieldInfo(alias="selectedRefinements", default=None)
    """A map of selected refinement attribute ID or value pairs.

    The sorting order is the same as in request URL.
    """

    selected_sorting_option: Optional[str] = FieldInfo(alias="selectedSortingOption", default=None)
    """
    The String4000 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 4000 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 4000
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      2000 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 1333 characters.
    """


from .product_search_refinement_value import ProductSearchRefinementValue
