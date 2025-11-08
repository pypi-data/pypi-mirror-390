# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["CategoryListParams"]


class CategoryListParams(TypedDict, total=False):
    ids: Required[SequenceNotStr[str]]
    """The comma separated list of category IDs (max 50)."""

    site_id: Required[Annotated[str, PropertyInfo(alias="siteId")]]
    """The identifier of the site that a request is being made in the context of.

    Attributes might have site specific values, and some objects may only be
    assigned to specific sites.
    """

    levels: Literal[0, 1, 2]
    """Specifies how many levels of nested subcategories you want the server to return.

    The default value is 1. Valid values are 0, 1, or 2. Only online subcategories
    are returned.
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
