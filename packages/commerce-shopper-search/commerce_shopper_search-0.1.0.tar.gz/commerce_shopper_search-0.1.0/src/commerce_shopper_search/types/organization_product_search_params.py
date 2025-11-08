# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .currency_code_param import CurrencyCodeParam

__all__ = ["OrganizationProductSearchParams"]


class OrganizationProductSearchParams(TypedDict, total=False):
    site_id: Required[Annotated[str, PropertyInfo(alias="siteId")]]
    """The identifier of the site that a request is being made in the context of.

    Attributes might have site specific values, and some objects may only be
    assigned to specific sites.
    """

    all_images: Annotated[bool, PropertyInfo(alias="allImages")]
    """
    When the `images` expand parameter is used with this flag, the response includes
    the `imageGroups property`, which contains an image model. If this flag is true,
    the full image model is returned. If false, only matching images are included.
    If no flag is passed, the `imageGroups` property is omitted from the response.
    """

    all_variation_properties: Annotated[bool, PropertyInfo(alias="allVariationProperties")]
    """The flag that determines which variation properties are included in the result.

    When set to `true` with the `variations` expand parameter, all variation
    properties (`variationAttributes`, `variationGroups`, `variants`) are returned.
    When set to false, only the default property `variationAttributes` is returned.
    """

    currency: CurrencyCodeParam
    """
    A three letter uppercase currency code conforming to the
    [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
    string `N/A` indicating that a currency is not applicable.
    """

    expand: List[
        Literal[
            "none",
            "availability",
            "images",
            "prices",
            "represented_products",
            "variations",
            "promotions",
            "custom_properties",
            "page_meta_tags",
        ]
    ]
    """
    A comma-separated list with allowed values - `availability`, `images`, `prices`,
    `represented_products`, `variations`, `promotions`, `custom_properties`. By
    default, the expand parameter includes
    `availability, images, prices, represented_products, variations`. Use none to
    disable all expand options. **The page_meta_tags expand value is optional and is
    available B2C Commerce version 25.2.**"
    """

    included_custom_variation_properties: Annotated[
        SequenceNotStr[str], PropertyInfo(alias="includedCustomVariationProperties")
    ]
    """
    A comma-separated list of custom property ids to be returned for variant
    products. The `variants` expand parameter and `allVariationProperties` query
    parameter are required for these properties to be returned.
    """

    limit: int
    """Maximum records to retrieve per request, not to exceed 200. Defaults to 25."""

    locale: Union[str, Literal["default"]]
    """A descriptor for a geographical region by both a language and country code.

    By combining these two, regional differences in a language can be addressed,
    such as with the request header parameter `Accept-Language` following
    [RFC 2616](https://tools.ietf.org/html/rfc2616) &
    [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
    language code, also RFC 2616/1766 compliant, as a default if there is no
    specific match for a country. Finally, can also be used to define default
    behavior if there is no locale specified.
    """

    offset: int
    """Used to retrieve the results based on a particular resource offset."""

    per_pricebook: Annotated[bool, PropertyInfo(alias="perPricebook")]
    """
    When this flag is set to `true` and is used with the `prices` expand parameter,
    the response includes per PriceBook prices and tiered prices (if available).
    """

    q: str
    """The query phrase to search for.

    For example to search for a product "shirt", type q=shirt.
    """

    refine: SequenceNotStr[str]
    """Parameter that represents a refinement attribute or values pair.

    Refinement attribute ID and values are separated by '='. Multiple values are
    supported by a subset of refinement attributes and can be provided by separating
    them using a pipe (URL encoded = \"|\") i.e.
    refine=c_refinementColor=red|green|blue. Value ranges can be specified like
    this: refine=price=(100..500) . Multiple refine parameters can be provided by
    using the refine as the key i.e
    refine=price=(0..10)&refine=c_refinementColor=green. The refinements can be a
    collection of custom defined attributes IDs and the system defined attributes
    IDs but the search can only accept a total of 9 refinements at a time.

    The following system refinement attribute ids are supported:

    `cgid`: Allows refinement per single category ID. Multiple category ids are not
    supported.
    `price`: Allows refinement per single price range. Multiple price ranges are not
    supported.
    `htype`: Allow refinement by including only the provided hit types. Accepted
    types are 'product', 'master', 'set', 'bundle', 'slicing_group' (deprecated),
    'variation_group'.

    `orderable_only`: Unavailable products are excluded from the search results if
    true is set. Multiple refinement values are not supported.

    `ilids`: Allows refining by inventory list IDs. Supports up to 10 inventory list
    IDs per request.

    `pmid`: Allows refinement on the supplied promotion ID(s). When used with
    `pmpt`, filters products by their role in the promotion.

    `pmpt`: Allows refinement per promotion product type. Must be used with `pmid`
    to filter products by their role in the promotion. Valid values are:

    - `all`: Returns all products related to the promotion (default)
    - `qualifying`: Returns only products that qualify for the promotion but don't
      receive the discount/bonus
    - `discounted`: Returns only products that receive a discount in the promotion
    - `bonus`: Returns only products that are given as bonuses in the promotion

    **Note:** To refine a search using multiple promotion filters—for example, to
    find products in both the spring and summer campaigns—see
    [Refining by Multiple Promotions](https://developer.salesforce.com/docs/commerce/b2c-commerce/guide/b2c-promotions-for-developers.html#refining-by-multiple-promotions).
    """

    select: str
    """
    The property selector declaring which fields are included into the response
    payload. You can specify a single field name, a comma-separated list of names or
    work with wildcards. You can also specify array operations and filter
    expressions. The actual selector value must be enclosed within parentheses.
    """

    sort: str
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
