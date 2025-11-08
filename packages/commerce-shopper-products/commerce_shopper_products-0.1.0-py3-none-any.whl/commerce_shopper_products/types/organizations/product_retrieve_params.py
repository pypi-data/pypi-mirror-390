# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union
from typing_extensions import Literal, Required, Annotated, TypedDict

from ..._types import SequenceNotStr
from ..._utils import PropertyInfo

__all__ = ["ProductRetrieveParams"]


class ProductRetrieveParams(TypedDict, total=False):
    organization_id: Required[Annotated[str, PropertyInfo(alias="organizationId")]]
    """An identifier for the organization the request is being made by"""

    site_id: Required[Annotated[str, PropertyInfo(alias="siteId")]]
    """The identifier of the site that a request is being made in the context of.

    Attributes might have site specific values, and some objects may only be
    assigned to specific sites.
    """

    all_images: Annotated[bool, PropertyInfo(alias="allImages")]
    """
    The flag that indicates whether to retrieve the whole image model for the
    requested product.
    """

    currency: Union[str, Literal["N/A"]]
    """
    A three letter uppercase currency code conforming to the
    [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
    string `N/A` indicating that a currency is not applicable.
    """

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
    """
    All expand parameters except page_meta_tags are used for the request when no
    expand parameter is provided. The value "none" may be used to turn off all
    expand options. The page_meta_tags expand value is optional and available
    starting from B2C Commerce version 25.2.
    """

    inventory_ids: Annotated[SequenceNotStr[str], PropertyInfo(alias="inventoryIds")]
    """
    The optional inventory list IDs, for which the availability should be shown
    (comma-separated, max 5 inventoryListIDs).
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

    per_pricebook: Annotated[bool, PropertyInfo(alias="perPricebook")]
    """
    The flag that indicates whether to retrieve the per PriceBook prices and tiered
    prices (if available) for requested Products. Available end of June, 2021.
    """

    select: str
    """
    The property selector declaring which fields are included into the response
    payload. You can specify a single field name, a comma-separated list of names or
    work with wildcards. You can also specify array operations and filter
    expressions. The actual selector value must be enclosed within parentheses.
    """
