# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._types import SequenceNotStr
from .._utils import PropertyInfo
from .currency_code_param import CurrencyCodeParam

__all__ = ["OrganizationSearchSuggestionsParams"]


class OrganizationSearchSuggestionsParams(TypedDict, total=False):
    q: Required[str]
    """The search phrase (q) for which suggestions are evaluated.

    Search suggestions are determined when the search phrase input is at least three
    (default) characters long. The value is configurable in the Business Manager.
    """

    site_id: Required[Annotated[str, PropertyInfo(alias="siteId")]]
    """The identifier of the site that a request is being made in the context of.

    Attributes might have site specific values, and some objects may only be
    assigned to specific sites.
    """

    currency: CurrencyCodeParam
    """
    A three letter uppercase currency code conforming to the
    [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
    string `N/A` indicating that a currency is not applicable.
    """

    expand: List[Literal["images", "prices", "custom_product_properties"]]
    """
    A comma-separated list that allows values `images`, `prices`,
    `custom_product_properties`. By default, the expand parameter includes `prices`.
    """

    included_custom_product_properties: Annotated[
        SequenceNotStr[str], PropertyInfo(alias="includedCustomProductProperties")
    ]
    """
    A comma-separated list of custom property ids to be returned for product
    suggestions. The `custom_product_properties` expand parameter is required for
    these properties to be returned.
    """

    include_einstein_suggested_phrases: Annotated[bool, PropertyInfo(alias="includeEinsteinSuggestedPhrases")]
    """
    The flag that determines whether or not to show recent and popular suggested
    phrases from Einstein.
    """

    limit: int
    """The maximum number of suggestions made per request.

    If no value is defined, by default five suggestions per suggestion type are
    evaluated. This affects all types of suggestions (category, product, brand, and
    custom suggestions).
    """

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
