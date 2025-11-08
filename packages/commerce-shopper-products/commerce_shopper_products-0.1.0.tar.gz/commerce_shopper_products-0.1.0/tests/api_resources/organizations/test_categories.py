# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from commerce_shopper_products import CommerceShopperProducts, AsyncCommerceShopperProducts
from commerce_shopper_products.types.organizations import (
    Category,
    CategoryListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestCategories:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CommerceShopperProducts) -> None:
        category = client.organizations.categories.retrieve(
            id="mens",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )
        assert_matches_type(Category, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: CommerceShopperProducts) -> None:
        category = client.organizations.categories.retrieve(
            id="mens",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
            levels=1,
            locale="en-US",
        )
        assert_matches_type(Category, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CommerceShopperProducts) -> None:
        response = client.organizations.categories.with_raw_response.retrieve(
            id="mens",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        category = response.parse()
        assert_matches_type(Category, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CommerceShopperProducts) -> None:
        with client.organizations.categories.with_streaming_response.retrieve(
            id="mens",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            category = response.parse()
            assert_matches_type(Category, category, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CommerceShopperProducts) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.organizations.categories.with_raw_response.retrieve(
                id="mens",
                organization_id="",
                site_id="RefArch",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.organizations.categories.with_raw_response.retrieve(
                id="",
                organization_id="f_ecom_zzxy_prd",
                site_id="RefArch",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: CommerceShopperProducts) -> None:
        category = client.organizations.categories.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["mens"],
            site_id="RefArch",
        )
        assert_matches_type(CategoryListResponse, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: CommerceShopperProducts) -> None:
        category = client.organizations.categories.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["mens"],
            site_id="RefArch",
            levels=1,
            locale="en-US",
        )
        assert_matches_type(CategoryListResponse, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: CommerceShopperProducts) -> None:
        response = client.organizations.categories.with_raw_response.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["mens"],
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        category = response.parse()
        assert_matches_type(CategoryListResponse, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: CommerceShopperProducts) -> None:
        with client.organizations.categories.with_streaming_response.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["mens"],
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            category = response.parse()
            assert_matches_type(CategoryListResponse, category, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: CommerceShopperProducts) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.organizations.categories.with_raw_response.list(
                organization_id="",
                ids=["mens"],
                site_id="RefArch",
            )


class TestAsyncCategories:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCommerceShopperProducts) -> None:
        category = await async_client.organizations.categories.retrieve(
            id="mens",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )
        assert_matches_type(Category, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncCommerceShopperProducts) -> None:
        category = await async_client.organizations.categories.retrieve(
            id="mens",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
            levels=1,
            locale="en-US",
        )
        assert_matches_type(Category, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCommerceShopperProducts) -> None:
        response = await async_client.organizations.categories.with_raw_response.retrieve(
            id="mens",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        category = await response.parse()
        assert_matches_type(Category, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCommerceShopperProducts) -> None:
        async with async_client.organizations.categories.with_streaming_response.retrieve(
            id="mens",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            category = await response.parse()
            assert_matches_type(Category, category, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCommerceShopperProducts) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.organizations.categories.with_raw_response.retrieve(
                id="mens",
                organization_id="",
                site_id="RefArch",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.organizations.categories.with_raw_response.retrieve(
                id="",
                organization_id="f_ecom_zzxy_prd",
                site_id="RefArch",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncCommerceShopperProducts) -> None:
        category = await async_client.organizations.categories.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["mens"],
            site_id="RefArch",
        )
        assert_matches_type(CategoryListResponse, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCommerceShopperProducts) -> None:
        category = await async_client.organizations.categories.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["mens"],
            site_id="RefArch",
            levels=1,
            locale="en-US",
        )
        assert_matches_type(CategoryListResponse, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCommerceShopperProducts) -> None:
        response = await async_client.organizations.categories.with_raw_response.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["mens"],
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        category = await response.parse()
        assert_matches_type(CategoryListResponse, category, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCommerceShopperProducts) -> None:
        async with async_client.organizations.categories.with_streaming_response.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["mens"],
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            category = await response.parse()
            assert_matches_type(CategoryListResponse, category, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncCommerceShopperProducts) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.organizations.categories.with_raw_response.list(
                organization_id="",
                ids=["mens"],
                site_id="RefArch",
            )
