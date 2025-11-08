# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from commerce_shopper_products import CommerceShopperProducts, AsyncCommerceShopperProducts
from commerce_shopper_products.types.organizations import (
    Product,
    ProductListResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProducts:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: CommerceShopperProducts) -> None:
        product = client.organizations.products.retrieve(
            id="apple-ipod-classic",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )
        assert_matches_type(Product, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_with_all_params(self, client: CommerceShopperProducts) -> None:
        product = client.organizations.products.retrieve(
            id="apple-ipod-classic",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
            all_images=True,
            currency="USD",
            expand=["prices", "promotions"],
            inventory_ids=["Site1InventoryList"],
            locale="en-US",
            per_pricebook=True,
            select="(name,id,variationAttributes.(**))",
        )
        assert_matches_type(Product, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: CommerceShopperProducts) -> None:
        response = client.organizations.products.with_raw_response.retrieve(
            id="apple-ipod-classic",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = response.parse()
        assert_matches_type(Product, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: CommerceShopperProducts) -> None:
        with client.organizations.products.with_streaming_response.retrieve(
            id="apple-ipod-classic",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = response.parse()
            assert_matches_type(Product, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: CommerceShopperProducts) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.organizations.products.with_raw_response.retrieve(
                id="apple-ipod-classic",
                organization_id="",
                site_id="RefArch",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.organizations.products.with_raw_response.retrieve(
                id="",
                organization_id="f_ecom_zzxy_prd",
                site_id="RefArch",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: CommerceShopperProducts) -> None:
        product = client.organizations.products.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["apple-ipod-classic"],
            site_id="RefArch",
        )
        assert_matches_type(ProductListResponse, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: CommerceShopperProducts) -> None:
        product = client.organizations.products.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["apple-ipod-classic"],
            site_id="RefArch",
            all_images=True,
            currency="USD",
            expand=["prices", "promotions"],
            inventory_ids=["Site1InventoryList"],
            locale="en-US",
            per_pricebook=True,
            select="(name,id,variationAttributes.(**))",
        )
        assert_matches_type(ProductListResponse, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: CommerceShopperProducts) -> None:
        response = client.organizations.products.with_raw_response.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["apple-ipod-classic"],
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = response.parse()
        assert_matches_type(ProductListResponse, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: CommerceShopperProducts) -> None:
        with client.organizations.products.with_streaming_response.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["apple-ipod-classic"],
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = response.parse()
            assert_matches_type(ProductListResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list(self, client: CommerceShopperProducts) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            client.organizations.products.with_raw_response.list(
                organization_id="",
                ids=["apple-ipod-classic"],
                site_id="RefArch",
            )


class TestAsyncProducts:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncCommerceShopperProducts) -> None:
        product = await async_client.organizations.products.retrieve(
            id="apple-ipod-classic",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )
        assert_matches_type(Product, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_with_all_params(self, async_client: AsyncCommerceShopperProducts) -> None:
        product = await async_client.organizations.products.retrieve(
            id="apple-ipod-classic",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
            all_images=True,
            currency="USD",
            expand=["prices", "promotions"],
            inventory_ids=["Site1InventoryList"],
            locale="en-US",
            per_pricebook=True,
            select="(name,id,variationAttributes.(**))",
        )
        assert_matches_type(Product, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncCommerceShopperProducts) -> None:
        response = await async_client.organizations.products.with_raw_response.retrieve(
            id="apple-ipod-classic",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = await response.parse()
        assert_matches_type(Product, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncCommerceShopperProducts) -> None:
        async with async_client.organizations.products.with_streaming_response.retrieve(
            id="apple-ipod-classic",
            organization_id="f_ecom_zzxy_prd",
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = await response.parse()
            assert_matches_type(Product, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncCommerceShopperProducts) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.organizations.products.with_raw_response.retrieve(
                id="apple-ipod-classic",
                organization_id="",
                site_id="RefArch",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.organizations.products.with_raw_response.retrieve(
                id="",
                organization_id="f_ecom_zzxy_prd",
                site_id="RefArch",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncCommerceShopperProducts) -> None:
        product = await async_client.organizations.products.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["apple-ipod-classic"],
            site_id="RefArch",
        )
        assert_matches_type(ProductListResponse, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncCommerceShopperProducts) -> None:
        product = await async_client.organizations.products.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["apple-ipod-classic"],
            site_id="RefArch",
            all_images=True,
            currency="USD",
            expand=["prices", "promotions"],
            inventory_ids=["Site1InventoryList"],
            locale="en-US",
            per_pricebook=True,
            select="(name,id,variationAttributes.(**))",
        )
        assert_matches_type(ProductListResponse, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncCommerceShopperProducts) -> None:
        response = await async_client.organizations.products.with_raw_response.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["apple-ipod-classic"],
            site_id="RefArch",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        product = await response.parse()
        assert_matches_type(ProductListResponse, product, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncCommerceShopperProducts) -> None:
        async with async_client.organizations.products.with_streaming_response.list(
            organization_id="f_ecom_zzxy_prd",
            ids=["apple-ipod-classic"],
            site_id="RefArch",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            product = await response.parse()
            assert_matches_type(ProductListResponse, product, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list(self, async_client: AsyncCommerceShopperProducts) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `organization_id` but received ''"):
            await async_client.organizations.products.with_raw_response.list(
                organization_id="",
                ids=["apple-ipod-classic"],
                site_id="RefArch",
            )
