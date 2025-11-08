# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal

import httpx

from ..._types import Body, Omit, Query, Headers, NotGiven, SequenceNotStr, omit, not_given
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.organizations import product_list_params, product_retrieve_params
from ...types.organizations.product import Product
from ...types.organizations.product_list_response import ProductListResponse

__all__ = ["ProductsResource", "AsyncProductsResource"]


class ProductsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProductsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-products#accessing-raw-response-data-eg-headers
        """
        return ProductsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProductsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-products#with_streaming_response
        """
        return ProductsResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        organization_id: str,
        site_id: str,
        all_images: bool | Omit = omit,
        currency: Union[str, Literal["N/A"]] | Omit = omit,
        expand: List[
            Literal[
                "none",
                "availability",
                "bundled_products",
                "links",
                "promotions",
                "options",
                "images",
                "prices",
                "variations",
                "set_products",
                "recommendations",
                "page_meta_tags",
            ]
        ]
        | Omit = omit,
        inventory_ids: SequenceNotStr[str] | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        per_pricebook: bool | Omit = omit,
        select: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Product:
        """Allows access to product details for a single product ID.

        Only products that are
        online and assigned to a site catalog are returned. In addition to product
        details, the availability, images, price, bundled_products, set_products,
        recommedations, product options, variations, and promotions for the products are
        included, as applicable.

        Args:
          organization_id: An identifier for the organization the request is being made by

          id: The id (SKU) of the product.

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          all_images: The flag that indicates whether to retrieve the whole image model for the
              requested product.

          currency: A three letter uppercase currency code conforming to the
              [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
              string `N/A` indicating that a currency is not applicable.

          expand: All expand parameters except page_meta_tags are used for the request when no
              expand parameter is provided. The value "none" may be used to turn off all
              expand options. The page_meta_tags expand value is optional and available
              starting from B2C Commerce version 25.2.

          inventory_ids: The optional inventory list IDs, for which the availability should be shown
              (comma-separated, max 5 inventoryListIDs).

          locale: A descriptor for a geographical region by both a language and country code. By
              combining these two, regional differences in a language can be addressed, such
              as with the request header parameter `Accept-Language` following
              [RFC 2616](https://tools.ietf.org/html/rfc2616) &
              [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
              language code, also RFC 2616/1766 compliant, as a default if there is no
              specific match for a country. Finally, can also be used to define default
              behavior if there is no locale specified.

          per_pricebook: The flag that indicates whether to retrieve the per PriceBook prices and tiered
              prices (if available) for requested Products. Available end of June, 2021.

          select: The property selector declaring which fields are included into the response
              payload. You can specify a single field name, a comma-separated list of names or
              work with wildcards. You can also specify array operations and filter
              expressions. The actual selector value must be enclosed within parentheses.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/organizations/{organization_id}/products/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "site_id": site_id,
                        "all_images": all_images,
                        "currency": currency,
                        "expand": expand,
                        "inventory_ids": inventory_ids,
                        "locale": locale,
                        "per_pricebook": per_pricebook,
                        "select": select,
                    },
                    product_retrieve_params.ProductRetrieveParams,
                ),
            ),
            cast_to=Product,
        )

    def list(
        self,
        organization_id: str,
        *,
        ids: SequenceNotStr[str],
        site_id: str,
        all_images: bool | Omit = omit,
        currency: Union[str, Literal["N/A"]] | Omit = omit,
        expand: List[
            Literal[
                "none",
                "availability",
                "links",
                "promotions",
                "options",
                "images",
                "prices",
                "variations",
                "recommendations",
                "page_meta_tags",
            ]
        ]
        | Omit = omit,
        inventory_ids: SequenceNotStr[str] | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        per_pricebook: bool | Omit = omit,
        select: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProductListResponse:
        """Allows access to multiple product details with a single request.

        Only products
        that are online and assigned to a site catalog are returned. The maximum number
        of product IDs that you can request is 24. In addition to product details, the
        availability, product options, images, price, promotions, and variations for the
        valid products are included, as applicable.

        Args:
          organization_id: An identifier for the organization the request is being made by

          ids: The IDs of the requested products (comma-separated, max 24 IDs).

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          all_images: The flag that indicates whether to retrieve the whole image model for the
              requested product.

          currency: A three letter uppercase currency code conforming to the
              [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
              string `N/A` indicating that a currency is not applicable.

          expand: All expand parameters except page_meta_tags are used for the request when no
              expand parameter is provided. The value "none" may be used to turn off all
              expand options. The page_meta_tags expand value is optional and available
              starting from B2C Commerce version 25.2.

          inventory_ids: The optional inventory list IDs, for which the availability should be shown
              (comma-separated, max 5 inventoryListIDs).

          locale: A descriptor for a geographical region by both a language and country code. By
              combining these two, regional differences in a language can be addressed, such
              as with the request header parameter `Accept-Language` following
              [RFC 2616](https://tools.ietf.org/html/rfc2616) &
              [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
              language code, also RFC 2616/1766 compliant, as a default if there is no
              specific match for a country. Finally, can also be used to define default
              behavior if there is no locale specified.

          per_pricebook: The flag that indicates whether to retrieve the per PriceBook prices and tiered
              prices (if available) for requested Products. Available end of June, 2021.

          select: The property selector declaring which fields are included into the response
              payload. You can specify a single field name, a comma-separated list of names or
              work with wildcards. You can also specify array operations and filter
              expressions. The actual selector value must be enclosed within parentheses.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return self._get(
            f"/organizations/{organization_id}/products",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "ids": ids,
                        "site_id": site_id,
                        "all_images": all_images,
                        "currency": currency,
                        "expand": expand,
                        "inventory_ids": inventory_ids,
                        "locale": locale,
                        "per_pricebook": per_pricebook,
                        "select": select,
                    },
                    product_list_params.ProductListParams,
                ),
            ),
            cast_to=ProductListResponse,
        )


class AsyncProductsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProductsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-products#accessing-raw-response-data-eg-headers
        """
        return AsyncProductsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProductsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-products#with_streaming_response
        """
        return AsyncProductsResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        organization_id: str,
        site_id: str,
        all_images: bool | Omit = omit,
        currency: Union[str, Literal["N/A"]] | Omit = omit,
        expand: List[
            Literal[
                "none",
                "availability",
                "bundled_products",
                "links",
                "promotions",
                "options",
                "images",
                "prices",
                "variations",
                "set_products",
                "recommendations",
                "page_meta_tags",
            ]
        ]
        | Omit = omit,
        inventory_ids: SequenceNotStr[str] | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        per_pricebook: bool | Omit = omit,
        select: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Product:
        """Allows access to product details for a single product ID.

        Only products that are
        online and assigned to a site catalog are returned. In addition to product
        details, the availability, images, price, bundled_products, set_products,
        recommedations, product options, variations, and promotions for the products are
        included, as applicable.

        Args:
          organization_id: An identifier for the organization the request is being made by

          id: The id (SKU) of the product.

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          all_images: The flag that indicates whether to retrieve the whole image model for the
              requested product.

          currency: A three letter uppercase currency code conforming to the
              [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
              string `N/A` indicating that a currency is not applicable.

          expand: All expand parameters except page_meta_tags are used for the request when no
              expand parameter is provided. The value "none" may be used to turn off all
              expand options. The page_meta_tags expand value is optional and available
              starting from B2C Commerce version 25.2.

          inventory_ids: The optional inventory list IDs, for which the availability should be shown
              (comma-separated, max 5 inventoryListIDs).

          locale: A descriptor for a geographical region by both a language and country code. By
              combining these two, regional differences in a language can be addressed, such
              as with the request header parameter `Accept-Language` following
              [RFC 2616](https://tools.ietf.org/html/rfc2616) &
              [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
              language code, also RFC 2616/1766 compliant, as a default if there is no
              specific match for a country. Finally, can also be used to define default
              behavior if there is no locale specified.

          per_pricebook: The flag that indicates whether to retrieve the per PriceBook prices and tiered
              prices (if available) for requested Products. Available end of June, 2021.

          select: The property selector declaring which fields are included into the response
              payload. You can specify a single field name, a comma-separated list of names or
              work with wildcards. You can also specify array operations and filter
              expressions. The actual selector value must be enclosed within parentheses.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/organizations/{organization_id}/products/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "site_id": site_id,
                        "all_images": all_images,
                        "currency": currency,
                        "expand": expand,
                        "inventory_ids": inventory_ids,
                        "locale": locale,
                        "per_pricebook": per_pricebook,
                        "select": select,
                    },
                    product_retrieve_params.ProductRetrieveParams,
                ),
            ),
            cast_to=Product,
        )

    async def list(
        self,
        organization_id: str,
        *,
        ids: SequenceNotStr[str],
        site_id: str,
        all_images: bool | Omit = omit,
        currency: Union[str, Literal["N/A"]] | Omit = omit,
        expand: List[
            Literal[
                "none",
                "availability",
                "links",
                "promotions",
                "options",
                "images",
                "prices",
                "variations",
                "recommendations",
                "page_meta_tags",
            ]
        ]
        | Omit = omit,
        inventory_ids: SequenceNotStr[str] | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        per_pricebook: bool | Omit = omit,
        select: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ProductListResponse:
        """Allows access to multiple product details with a single request.

        Only products
        that are online and assigned to a site catalog are returned. The maximum number
        of product IDs that you can request is 24. In addition to product details, the
        availability, product options, images, price, promotions, and variations for the
        valid products are included, as applicable.

        Args:
          organization_id: An identifier for the organization the request is being made by

          ids: The IDs of the requested products (comma-separated, max 24 IDs).

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          all_images: The flag that indicates whether to retrieve the whole image model for the
              requested product.

          currency: A three letter uppercase currency code conforming to the
              [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
              string `N/A` indicating that a currency is not applicable.

          expand: All expand parameters except page_meta_tags are used for the request when no
              expand parameter is provided. The value "none" may be used to turn off all
              expand options. The page_meta_tags expand value is optional and available
              starting from B2C Commerce version 25.2.

          inventory_ids: The optional inventory list IDs, for which the availability should be shown
              (comma-separated, max 5 inventoryListIDs).

          locale: A descriptor for a geographical region by both a language and country code. By
              combining these two, regional differences in a language can be addressed, such
              as with the request header parameter `Accept-Language` following
              [RFC 2616](https://tools.ietf.org/html/rfc2616) &
              [RFC 1766](https://tools.ietf.org/html/rfc1766). This can also just refer to a
              language code, also RFC 2616/1766 compliant, as a default if there is no
              specific match for a country. Finally, can also be used to define default
              behavior if there is no locale specified.

          per_pricebook: The flag that indicates whether to retrieve the per PriceBook prices and tiered
              prices (if available) for requested Products. Available end of June, 2021.

          select: The property selector declaring which fields are included into the response
              payload. You can specify a single field name, a comma-separated list of names or
              work with wildcards. You can also specify array operations and filter
              expressions. The actual selector value must be enclosed within parentheses.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not organization_id:
            raise ValueError(f"Expected a non-empty value for `organization_id` but received {organization_id!r}")
        return await self._get(
            f"/organizations/{organization_id}/products",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "ids": ids,
                        "site_id": site_id,
                        "all_images": all_images,
                        "currency": currency,
                        "expand": expand,
                        "inventory_ids": inventory_ids,
                        "locale": locale,
                        "per_pricebook": per_pricebook,
                        "select": select,
                    },
                    product_list_params.ProductListParams,
                ),
            ),
            cast_to=ProductListResponse,
        )


class ProductsResourceWithRawResponse:
    def __init__(self, products: ProductsResource) -> None:
        self._products = products

        self.retrieve = to_raw_response_wrapper(
            products.retrieve,
        )
        self.list = to_raw_response_wrapper(
            products.list,
        )


class AsyncProductsResourceWithRawResponse:
    def __init__(self, products: AsyncProductsResource) -> None:
        self._products = products

        self.retrieve = async_to_raw_response_wrapper(
            products.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            products.list,
        )


class ProductsResourceWithStreamingResponse:
    def __init__(self, products: ProductsResource) -> None:
        self._products = products

        self.retrieve = to_streamed_response_wrapper(
            products.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            products.list,
        )


class AsyncProductsResourceWithStreamingResponse:
    def __init__(self, products: AsyncProductsResource) -> None:
        self._products = products

        self.retrieve = async_to_streamed_response_wrapper(
            products.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            products.list,
        )
