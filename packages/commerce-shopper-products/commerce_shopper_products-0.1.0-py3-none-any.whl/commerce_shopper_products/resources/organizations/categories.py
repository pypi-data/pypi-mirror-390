# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
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
from ...types.organizations import category_list_params, category_retrieve_params
from ...types.organizations.category import Category
from ...types.organizations.category_list_response import CategoryListResponse

__all__ = ["CategoriesResource", "AsyncCategoriesResource"]


class CategoriesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> CategoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-products#accessing-raw-response-data-eg-headers
        """
        return CategoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> CategoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-products#with_streaming_response
        """
        return CategoriesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        organization_id: str,
        site_id: str,
        levels: Literal[0, 1, 2] | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Category:
        """
        When you use the URL template, the server returns a category identified by the
        ID. By default, the server also returns the first level of subcategories, but
        you can specify an additional level using the levels parameter.

        This endpoint fetches both online and offline categories. For offline
        categories, only the top-level category is returned, not offline subcategories.

        Using a large value for levels can cause performance issues when there is a
        large and deep category tree.

        Args:
          organization_id: An identifier for the organization the request is being made by

          id: The ID of the category.

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          levels: Specifies how many levels of nested subcategories you want the server to return.
              The default value is 1. Valid values are 0, 1, or 2. Only online subcategories
              are returned.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/organizations/{organization_id}/categories/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "site_id": site_id,
                        "levels": levels,
                        "locale": locale,
                    },
                    category_retrieve_params.CategoryRetrieveParams,
                ),
            ),
            cast_to=Category,
        )

    def list(
        self,
        organization_id: str,
        *,
        ids: SequenceNotStr[str],
        site_id: str,
        levels: Literal[0, 1, 2] | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CategoryListResponse:
        """
        When you use the URL template, the server returns multiple categories (a result
        object of category documents). You can use this template to obtain up to 50
        categories in a single request. You must enclose the list of IDs in parentheses.
        If a category identifier contains parenthesis or the separator sign, you must
        URL encode the character.

        Args:
          organization_id: An identifier for the organization the request is being made by

          ids: The comma separated list of category IDs (max 50).

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          levels: Specifies how many levels of nested subcategories you want the server to return.
              The default value is 1. Valid values are 0, 1, or 2. Only online subcategories
              are returned.

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
            f"/organizations/{organization_id}/categories",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "ids": ids,
                        "site_id": site_id,
                        "levels": levels,
                        "locale": locale,
                    },
                    category_list_params.CategoryListParams,
                ),
            ),
            cast_to=CategoryListResponse,
        )


class AsyncCategoriesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncCategoriesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-products#accessing-raw-response-data-eg-headers
        """
        return AsyncCategoriesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncCategoriesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/botbrains-io/commerce-shopper-products#with_streaming_response
        """
        return AsyncCategoriesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        organization_id: str,
        site_id: str,
        levels: Literal[0, 1, 2] | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> Category:
        """
        When you use the URL template, the server returns a category identified by the
        ID. By default, the server also returns the first level of subcategories, but
        you can specify an additional level using the levels parameter.

        This endpoint fetches both online and offline categories. For offline
        categories, only the top-level category is returned, not offline subcategories.

        Using a large value for levels can cause performance issues when there is a
        large and deep category tree.

        Args:
          organization_id: An identifier for the organization the request is being made by

          id: The ID of the category.

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          levels: Specifies how many levels of nested subcategories you want the server to return.
              The default value is 1. Valid values are 0, 1, or 2. Only online subcategories
              are returned.

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
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/organizations/{organization_id}/categories/{id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "site_id": site_id,
                        "levels": levels,
                        "locale": locale,
                    },
                    category_retrieve_params.CategoryRetrieveParams,
                ),
            ),
            cast_to=Category,
        )

    async def list(
        self,
        organization_id: str,
        *,
        ids: SequenceNotStr[str],
        site_id: str,
        levels: Literal[0, 1, 2] | Omit = omit,
        locale: Union[str, Literal["default"]] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> CategoryListResponse:
        """
        When you use the URL template, the server returns multiple categories (a result
        object of category documents). You can use this template to obtain up to 50
        categories in a single request. You must enclose the list of IDs in parentheses.
        If a category identifier contains parenthesis or the separator sign, you must
        URL encode the character.

        Args:
          organization_id: An identifier for the organization the request is being made by

          ids: The comma separated list of category IDs (max 50).

          site_id: The identifier of the site that a request is being made in the context of.
              Attributes might have site specific values, and some objects may only be
              assigned to specific sites.

          levels: Specifies how many levels of nested subcategories you want the server to return.
              The default value is 1. Valid values are 0, 1, or 2. Only online subcategories
              are returned.

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
            f"/organizations/{organization_id}/categories",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "ids": ids,
                        "site_id": site_id,
                        "levels": levels,
                        "locale": locale,
                    },
                    category_list_params.CategoryListParams,
                ),
            ),
            cast_to=CategoryListResponse,
        )


class CategoriesResourceWithRawResponse:
    def __init__(self, categories: CategoriesResource) -> None:
        self._categories = categories

        self.retrieve = to_raw_response_wrapper(
            categories.retrieve,
        )
        self.list = to_raw_response_wrapper(
            categories.list,
        )


class AsyncCategoriesResourceWithRawResponse:
    def __init__(self, categories: AsyncCategoriesResource) -> None:
        self._categories = categories

        self.retrieve = async_to_raw_response_wrapper(
            categories.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            categories.list,
        )


class CategoriesResourceWithStreamingResponse:
    def __init__(self, categories: CategoriesResource) -> None:
        self._categories = categories

        self.retrieve = to_streamed_response_wrapper(
            categories.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            categories.list,
        )


class AsyncCategoriesResourceWithStreamingResponse:
    def __init__(self, categories: AsyncCategoriesResource) -> None:
        self._categories = categories

        self.retrieve = async_to_streamed_response_wrapper(
            categories.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            categories.list,
        )
