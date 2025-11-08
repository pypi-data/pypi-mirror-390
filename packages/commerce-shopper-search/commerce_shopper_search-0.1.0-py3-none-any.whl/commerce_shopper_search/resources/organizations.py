# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal

import httpx

from ..types import organization_product_search_params, organization_search_suggestions_params
from .._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.currency_code_param import CurrencyCodeParam
from ..types.organization_product_search_response import OrganizationProductSearchResponse
from ..types.organization_search_suggestions_response import OrganizationSearchSuggestionsResponse

__all__ = ["OrganizationsResource", "AsyncOrganizationsResource"]


class OrganizationsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> OrganizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-search#accessing-raw-response-data-eg-headers
        """
        return OrganizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> OrganizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-search#with_streaming_response
        """
        return OrganizationsResourceWithStreamingResponse(self)

    def product_search(
        self,
        organization_id: str,
        *,
        site_id: str,
        all_images: bool | Omit = omit,
        all_variation_properties: bool | Omit = omit,
        currency: CurrencyCodeParam | Omit = omit,
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
        | Omit = omit,
        included_custom_variation_properties: SequenceNotStr[str] | Omit = omit,
        limit: int | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        offset: int | Omit = omit,
        per_pricebook: bool | Omit = omit,
        q: str | Omit = omit,
        refine: SequenceNotStr[str] | Omit = omit,
        select: str | Omit = omit,
        sort: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationProductSearchResponse:
        """Provide keyword and refinement search functionality for products.

        Only returns
        the product ID, link, and name in the product search hit. The search result only
        contains products that are online and assigned to the site catalog.

        Args:
          organization_id: An identifier for the organization the request is being made by

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          all_images: When the `images` expand parameter is used with this flag, the response includes
              the `imageGroups property`, which contains an image model. If this flag is true,
              the full image model is returned. If false, only matching images are included.
              If no flag is passed, the `imageGroups` property is omitted from the response.

          all_variation_properties: The flag that determines which variation properties are included in the result.
              When set to `true` with the `variations` expand parameter, all variation
              properties (`variationAttributes`, `variationGroups`, `variants`) are returned.
              When set to false, only the default property `variationAttributes` is returned.

          currency: A three letter uppercase currency code conforming to the
              [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
              string `N/A` indicating that a currency is not applicable.

          expand: A comma-separated list with allowed values - `availability`, `images`, `prices`,
              `represented_products`, `variations`, `promotions`, `custom_properties`. By
              default, the expand parameter includes
              `availability, images, prices, represented_products, variations`. Use none to
              disable all expand options. **The page_meta_tags expand value is optional and is
              available B2C Commerce version 25.2.**"

          included_custom_variation_properties: A comma-separated list of custom property ids to be returned for variant
              products. The `variants` expand parameter and `allVariationProperties` query
              parameter are required for these properties to be returned.

          limit: Maximum records to retrieve per request, not to exceed 200. Defaults to 25.

          locale: A descriptor for a geographical region by both a language and country code. By
              combining these two, regional differences in a language can be addressed, such
              as with the request header parameter `Accept-Language` following
              [RFC 2616](https://tools.ietf.org/html/rfc2616) &
              [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
              language code, also RFC 2616/1766 compliant, as a default if there is no
              specific match for a country. Finally, can also be used to define default
              behavior if there is no locale specified.

          offset: Used to retrieve the results based on a particular resource offset.

          per_pricebook: When this flag is set to `true` and is used with the `prices` expand parameter,
              the response includes per PriceBook prices and tiered prices (if available).

          q: The query phrase to search for. For example to search for a product "shirt",
              type q=shirt.

          refine: Parameter that represents a refinement attribute or values pair. Refinement
              attribute ID and values are separated by '='. Multiple values are supported by a
              subset of refinement attributes and can be provided by separating them using a
              pipe (URL encoded = \"|\") i.e. refine=c_refinementColor=red|green|blue. Value
              ranges can be specified like this: refine=price=(100..500) . Multiple refine
              parameters can be provided by using the refine as the key i.e
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

          select: The property selector declaring which fields are included into the response
              payload. You can specify a single field name, a comma-separated list of names or
              work with wildcards. You can also specify array operations and filter
              expressions. The actual selector value must be enclosed within parentheses.

          sort: The String256 schema is a foundational schema designed for fields or attributes
              that are stored in a database field with a maximum capacity of 256 bytes. This
              schema accommodates various character sets, with the following considerations:

              - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
                characters.
              - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
                128 characters.
              - Asian Characters: Many Asian characters require 3 bytes each, allowing
                approximately 85 characters.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._get(
            f"/organizations/{organization_id}/product-search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "site_id": site_id,
                        "all_images": all_images,
                        "all_variation_properties": all_variation_properties,
                        "currency": currency,
                        "expand": expand,
                        "included_custom_variation_properties": included_custom_variation_properties,
                        "limit": limit,
                        "locale": locale,
                        "offset": offset,
                        "per_pricebook": per_pricebook,
                        "q": q,
                        "refine": refine,
                        "select": select,
                        "sort": sort,
                    },
                    organization_product_search_params.OrganizationProductSearchParams,
                ),
            ),
            cast_to=OrganizationProductSearchResponse,
        )

    def search_suggestions(
        self,
        organization_id: str,
        *,
        q: str,
        site_id: str,
        currency: CurrencyCodeParam | Omit = omit,
        expand: List[Literal["images", "prices", "custom_product_properties"]] | Omit = omit,
        included_custom_product_properties: SequenceNotStr[str] | Omit = omit,
        include_einstein_suggested_phrases: bool | Omit = omit,
        limit: int | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSearchSuggestionsResponse:
        """
        Provide keyword search functionality for products, categories, and brands
        suggestions. Returns suggested products, suggested categories, and suggested
        brands for the given search phrase.

        Args:
          organization_id: An identifier for the organization the request is being made by

          q: The search phrase (q) for which suggestions are evaluated. Search suggestions
              are determined when the search phrase input is at least three (default)
              characters long. The value is configurable in the Business Manager.

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          currency: A three letter uppercase currency code conforming to the
              [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
              string `N/A` indicating that a currency is not applicable.

          expand: A comma-separated list that allows values `images`, `prices`,
              `custom_product_properties`. By default, the expand parameter includes `prices`.

          included_custom_product_properties: A comma-separated list of custom property ids to be returned for product
              suggestions. The `custom_product_properties` expand parameter is required for
              these properties to be returned.

          include_einstein_suggested_phrases: The flag that determines whether or not to show recent and popular suggested
              phrases from Einstein.

          limit: The maximum number of suggestions made per request. If no value is defined, by
              default five suggestions per suggestion type are evaluated. This affects all
              types of suggestions (category, product, brand, and custom suggestions).

          locale: A descriptor for a geographical region by both a language and country code. By
              combining these two, regional differences in a language can be addressed, such
              as with the request header parameter `Accept-Language` following
              [RFC 2616](https://tools.ietf.org/html/rfc2616) &
              [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
              language code, also RFC 2616/1766 compliant, as a default if there is no
              specific match for a country. Finally, can also be used to define default
              behavior if there is no locale specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._get(
            f"/organizations/{organization_id}/search-suggestions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "q": q,
                        "site_id": site_id,
                        "currency": currency,
                        "expand": expand,
                        "included_custom_product_properties": included_custom_product_properties,
                        "include_einstein_suggested_phrases": include_einstein_suggested_phrases,
                        "limit": limit,
                        "locale": locale,
                    },
                    organization_search_suggestions_params.OrganizationSearchSuggestionsParams,
                ),
            ),
            cast_to=OrganizationSearchSuggestionsResponse,
        )


class AsyncOrganizationsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncOrganizationsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-search#accessing-raw-response-data-eg-headers
        """
        return AsyncOrganizationsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncOrganizationsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-search#with_streaming_response
        """
        return AsyncOrganizationsResourceWithStreamingResponse(self)

    async def product_search(
        self,
        organization_id: str,
        *,
        site_id: str,
        all_images: bool | Omit = omit,
        all_variation_properties: bool | Omit = omit,
        currency: CurrencyCodeParam | Omit = omit,
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
        | Omit = omit,
        included_custom_variation_properties: SequenceNotStr[str] | Omit = omit,
        limit: int | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        offset: int | Omit = omit,
        per_pricebook: bool | Omit = omit,
        q: str | Omit = omit,
        refine: SequenceNotStr[str] | Omit = omit,
        select: str | Omit = omit,
        sort: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationProductSearchResponse:
        """Provide keyword and refinement search functionality for products.

        Only returns
        the product ID, link, and name in the product search hit. The search result only
        contains products that are online and assigned to the site catalog.

        Args:
          organization_id: An identifier for the organization the request is being made by

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          all_images: When the `images` expand parameter is used with this flag, the response includes
              the `imageGroups property`, which contains an image model. If this flag is true,
              the full image model is returned. If false, only matching images are included.
              If no flag is passed, the `imageGroups` property is omitted from the response.

          all_variation_properties: The flag that determines which variation properties are included in the result.
              When set to `true` with the `variations` expand parameter, all variation
              properties (`variationAttributes`, `variationGroups`, `variants`) are returned.
              When set to false, only the default property `variationAttributes` is returned.

          currency: A three letter uppercase currency code conforming to the
              [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
              string `N/A` indicating that a currency is not applicable.

          expand: A comma-separated list with allowed values - `availability`, `images`, `prices`,
              `represented_products`, `variations`, `promotions`, `custom_properties`. By
              default, the expand parameter includes
              `availability, images, prices, represented_products, variations`. Use none to
              disable all expand options. **The page_meta_tags expand value is optional and is
              available B2C Commerce version 25.2.**"

          included_custom_variation_properties: A comma-separated list of custom property ids to be returned for variant
              products. The `variants` expand parameter and `allVariationProperties` query
              parameter are required for these properties to be returned.

          limit: Maximum records to retrieve per request, not to exceed 200. Defaults to 25.

          locale: A descriptor for a geographical region by both a language and country code. By
              combining these two, regional differences in a language can be addressed, such
              as with the request header parameter `Accept-Language` following
              [RFC 2616](https://tools.ietf.org/html/rfc2616) &
              [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
              language code, also RFC 2616/1766 compliant, as a default if there is no
              specific match for a country. Finally, can also be used to define default
              behavior if there is no locale specified.

          offset: Used to retrieve the results based on a particular resource offset.

          per_pricebook: When this flag is set to `true` and is used with the `prices` expand parameter,
              the response includes per PriceBook prices and tiered prices (if available).

          q: The query phrase to search for. For example to search for a product "shirt",
              type q=shirt.

          refine: Parameter that represents a refinement attribute or values pair. Refinement
              attribute ID and values are separated by '='. Multiple values are supported by a
              subset of refinement attributes and can be provided by separating them using a
              pipe (URL encoded = \"|\") i.e. refine=c_refinementColor=red|green|blue. Value
              ranges can be specified like this: refine=price=(100..500) . Multiple refine
              parameters can be provided by using the refine as the key i.e
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

          select: The property selector declaring which fields are included into the response
              payload. You can specify a single field name, a comma-separated list of names or
              work with wildcards. You can also specify array operations and filter
              expressions. The actual selector value must be enclosed within parentheses.

          sort: The String256 schema is a foundational schema designed for fields or attributes
              that are stored in a database field with a maximum capacity of 256 bytes. This
              schema accommodates various character sets, with the following considerations:

              - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
                characters.
              - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
                128 characters.
              - Asian Characters: Many Asian characters require 3 bytes each, allowing
                approximately 85 characters.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return await self._get(
            f"/organizations/{organization_id}/product-search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "site_id": site_id,
                        "all_images": all_images,
                        "all_variation_properties": all_variation_properties,
                        "currency": currency,
                        "expand": expand,
                        "included_custom_variation_properties": included_custom_variation_properties,
                        "limit": limit,
                        "locale": locale,
                        "offset": offset,
                        "per_pricebook": per_pricebook,
                        "q": q,
                        "refine": refine,
                        "select": select,
                        "sort": sort,
                    },
                    organization_product_search_params.OrganizationProductSearchParams,
                ),
            ),
            cast_to=OrganizationProductSearchResponse,
        )

    async def search_suggestions(
        self,
        organization_id: str,
        *,
        q: str,
        site_id: str,
        currency: CurrencyCodeParam | Omit = omit,
        expand: List[Literal["images", "prices", "custom_product_properties"]] | Omit = omit,
        included_custom_product_properties: SequenceNotStr[str] | Omit = omit,
        include_einstein_suggested_phrases: bool | Omit = omit,
        limit: int | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> OrganizationSearchSuggestionsResponse:
        """
        Provide keyword search functionality for products, categories, and brands
        suggestions. Returns suggested products, suggested categories, and suggested
        brands for the given search phrase.

        Args:
          organization_id: An identifier for the organization the request is being made by

          q: The search phrase (q) for which suggestions are evaluated. Search suggestions
              are determined when the search phrase input is at least three (default)
              characters long. The value is configurable in the Business Manager.

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          currency: A three letter uppercase currency code conforming to the
              [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
              string `N/A` indicating that a currency is not applicable.

          expand: A comma-separated list that allows values `images`, `prices`,
              `custom_product_properties`. By default, the expand parameter includes `prices`.

          included_custom_product_properties: A comma-separated list of custom property ids to be returned for product
              suggestions. The `custom_product_properties` expand parameter is required for
              these properties to be returned.

          include_einstein_suggested_phrases: The flag that determines whether or not to show recent and popular suggested
              phrases from Einstein.

          limit: The maximum number of suggestions made per request. If no value is defined, by
              default five suggestions per suggestion type are evaluated. This affects all
              types of suggestions (category, product, brand, and custom suggestions).

          locale: A descriptor for a geographical region by both a language and country code. By
              combining these two, regional differences in a language can be addressed, such
              as with the request header parameter `Accept-Language` following
              [RFC 2616](https://tools.ietf.org/html/rfc2616) &
              [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
              language code, also RFC 2616/1766 compliant, as a default if there is no
              specific match for a country. Finally, can also be used to define default
              behavior if there is no locale specified.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return await self._get(
            f"/organizations/{organization_id}/search-suggestions",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "q": q,
                        "site_id": site_id,
                        "currency": currency,
                        "expand": expand,
                        "included_custom_product_properties": included_custom_product_properties,
                        "include_einstein_suggested_phrases": include_einstein_suggested_phrases,
                        "limit": limit,
                        "locale": locale,
                    },
                    organization_search_suggestions_params.OrganizationSearchSuggestionsParams,
                ),
            ),
            cast_to=OrganizationSearchSuggestionsResponse,
        )


class OrganizationsResourceWithRawResponse:
    def __init__(self, organizations: OrganizationsResource) -> None:
        self._organizations = organizations

        self.product_search = to_raw_response_wrapper(
            organizations.product_search,
        )
        self.search_suggestions = to_raw_response_wrapper(
            organizations.search_suggestions,
        )


class AsyncOrganizationsResourceWithRawResponse:
    def __init__(self, organizations: AsyncOrganizationsResource) -> None:
        self._organizations = organizations

        self.product_search = async_to_raw_response_wrapper(
            organizations.product_search,
        )
        self.search_suggestions = async_to_raw_response_wrapper(
            organizations.search_suggestions,
        )


class OrganizationsResourceWithStreamingResponse:
    def __init__(self, organizations: OrganizationsResource) -> None:
        self._organizations = organizations

        self.product_search = to_streamed_response_wrapper(
            organizations.product_search,
        )
        self.search_suggestions = to_streamed_response_wrapper(
            organizations.search_suggestions,
        )


class AsyncOrganizationsResourceWithStreamingResponse:
    def __init__(self, organizations: AsyncOrganizationsResource) -> None:
        self._organizations = organizations

        self.product_search = async_to_streamed_response_wrapper(
            organizations.product_search,
        )
        self.search_suggestions = async_to_streamed_response_wrapper(
            organizations.search_suggestions,
        )
