# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from commerce_shopper_search import CommerceShopperSearch, AsyncCommerceShopperSearch
from commerce_shopper_search.types import (
    OrganizationProductSearchResponse,
    OrganizationSearchSuggestionsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestOrganizations:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_product_search(self, client: CommerceShopperSearch) -> None:
        organization = client.organizations.product_search(
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )
        assert_matches_type(OrganizationProductSearchResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_product_search_with_all_params(self, client: CommerceShopperSearch) -> None:
        organization = client.organizations.product_search(
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
            all_images=True,
            all_variation_properties=False,
            currency="USD",
            expand=["prices"],
            included_custom_variation_properties=["Max Mustermann"],
            limit=200,
            locale="en-US",
            offset=0,
            per_pricebook=True,
            q="shirt",
            refine=["price=(0..10)", "c_refinementColor=green"],
            select="(name,id,variationAttributes.(**))",
            sort="Max Mustermann",
        )
        assert_matches_type(OrganizationProductSearchResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_product_search(self, client: CommerceShopperSearch) -> None:
        response = client.organizations.with_raw_response.product_search(
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        organization = response.parse()
        assert_matches_type(OrganizationProductSearchResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_product_search(self, client: CommerceShopperSearch) -> None:
        with client.organizations.with_streaming_response.product_search(
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            organization = response.parse()
            assert_matches_type(OrganizationProductSearchResponse, organization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_product_search(self, client: CommerceShopperSearch) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.organizations.with_raw_response.product_search(
                organization_id="",
                site_id="RefArch",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search_suggestions(self, client: CommerceShopperSearch) -> None:
        organization = client.organizations.search_suggestions(
            organization_id="f_ecom_zzxy_prd",
            q="sho",
            site_id="RefArch",
        )
        assert_matches_type(OrganizationSearchSuggestionsResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search_suggestions_with_all_params(self, client: CommerceShopperSearch) -> None:
        organization = client.organizations.search_suggestions(
            organization_id="f_ecom_zzxy_prd",
            q="sho",
            site_id="RefArch",
            currency="USD",
            expand=["prices"],
            included_custom_product_properties=["Max Mustermann"],
            include_einstein_suggested_phrases=False,
            limit=5,
            locale="en-US",
        )
        assert_matches_type(OrganizationSearchSuggestionsResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_search_suggestions(self, client: CommerceShopperSearch) -> None:
        response = client.organizations.with_raw_response.search_suggestions(
            organization_id="f_ecom_zzxy_prd",
            q="sho",
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        organization = response.parse()
        assert_matches_type(OrganizationSearchSuggestionsResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_search_suggestions(self, client: CommerceShopperSearch) -> None:
        with client.organizations.with_streaming_response.search_suggestions(
            organization_id="f_ecom_zzxy_prd",
            q="sho",
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            organization = response.parse()
            assert_matches_type(OrganizationSearchSuggestionsResponse, organization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_search_suggestions(self, client: CommerceShopperSearch) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.organizations.with_raw_response.search_suggestions(
                organization_id="",
                q="sho",
                site_id="RefArch",
            )


class TestAsyncOrganizations:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_product_search(self, async_client: AsyncCommerceShopperSearch) -> None:
        organization = await async_client.organizations.product_search(
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )
        assert_matches_type(OrganizationProductSearchResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_product_search_with_all_params(self, async_client: AsyncCommerceShopperSearch) -> None:
        organization = await async_client.organizations.product_search(
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
            all_images=True,
            all_variation_properties=False,
            currency="USD",
            expand=["prices"],
            included_custom_variation_properties=["Max Mustermann"],
            limit=200,
            locale="en-US",
            offset=0,
            per_pricebook=True,
            q="shirt",
            refine=["price=(0..10)", "c_refinementColor=green"],
            select="(name,id,variationAttributes.(**))",
            sort="Max Mustermann",
        )
        assert_matches_type(OrganizationProductSearchResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_product_search(self, async_client: AsyncCommerceShopperSearch) -> None:
        response = await async_client.organizations.with_raw_response.product_search(
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        organization = await response.parse()
        assert_matches_type(OrganizationProductSearchResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_product_search(self, async_client: AsyncCommerceShopperSearch) -> None:
        async with async_client.organizations.with_streaming_response.product_search(
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            organization = await response.parse()
            assert_matches_type(OrganizationProductSearchResponse, organization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_product_search(self, async_client: AsyncCommerceShopperSearch) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.organizations.with_raw_response.product_search(
                organization_id="",
                site_id="RefArch",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search_suggestions(self, async_client: AsyncCommerceShopperSearch) -> None:
        organization = await async_client.organizations.search_suggestions(
            organization_id="f_ecom_zzxy_prd",
            q="sho",
            site_id="RefArch",
        )
        assert_matches_type(OrganizationSearchSuggestionsResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search_suggestions_with_all_params(self, async_client: AsyncCommerceShopperSearch) -> None:
        organization = await async_client.organizations.search_suggestions(
            organization_id="f_ecom_zzxy_prd",
            q="sho",
            site_id="RefArch",
            currency="USD",
            expand=["prices"],
            included_custom_product_properties=["Max Mustermann"],
            include_einstein_suggested_phrases=False,
            limit=5,
            locale="en-US",
        )
        assert_matches_type(OrganizationSearchSuggestionsResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_search_suggestions(self, async_client: AsyncCommerceShopperSearch) -> None:
        response = await async_client.organizations.with_raw_response.search_suggestions(
            organization_id="f_ecom_zzxy_prd",
            q="sho",
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        organization = await response.parse()
        assert_matches_type(OrganizationSearchSuggestionsResponse, organization, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_search_suggestions(self, async_client: AsyncCommerceShopperSearch) -> None:
        async with async_client.organizations.with_streaming_response.search_suggestions(
            organization_id="f_ecom_zzxy_prd",
            q="sho",
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            organization = await response.parse()
            assert_matches_type(OrganizationSearchSuggestionsResponse, organization, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_search_suggestions(self, async_client: AsyncCommerceShopperSearch) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.organizations.with_raw_response.search_suggestions(
                organization_id="",
                q="sho",
                site_id="RefArch",
            )
