# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .image import Image
from ..._models import BaseModel
from .inventory import Inventory
from .product_price_table import ProductPriceTable
from .variation_attribute import VariationAttribute

__all__ = [
    "Product",
    "ImageGroup",
    "Master",
    "Option",
    "OptionValue",
    "PageMetaTag",
    "PriceRange",
    "ProductLink",
    "ProductPromotion",
    "Recommendation",
    "RecommendationRecommendationType",
    "Type",
    "Variant",
    "VariationGroup",
]


class ImageGroup(BaseModel):
    images: List[Image]
    """The images of the image group."""

    view_type: str = FieldInfo(alias="viewType")
    """The image view type."""

    variation_attributes: Optional[List[VariationAttribute]] = FieldInfo(alias="variationAttributes", default=None)
    """Returns a list of variation attributes applying to this image group."""


class Master(BaseModel):
    master_id: str = FieldInfo(alias="masterId")
    """The id (SKU) of the product."""

    orderable: Optional[bool] = None
    """A flag indicating whether at least one of the variants can be ordered."""

    price: Optional[float] = None
    """Document representing a price for a product"""

    price_max: Optional[float] = FieldInfo(alias="priceMax", default=None)
    """Document representing a price for a product"""

    prices: Optional[Dict[str, float]] = None
    """List of sale prices."""


class OptionValue(BaseModel):
    id: str
    """The id (SKU) of the product."""

    default: Optional[bool] = None
    """A flag indicating whether this option value is the default one."""

    name: Optional[str] = None
    """The localized name of the option value."""

    price: Optional[float] = None
    """Document representing a price for a product"""


class Option(BaseModel):
    id: str
    """The id (SKU) of the product."""

    description: Optional[str] = None
    """The localized description of the option."""

    image: Optional[str] = None
    """The URL to the option image."""

    name: Optional[str] = None
    """The localized name of the option."""

    values: Optional[List[OptionValue]] = None
    """The array of option values. This array can be empty."""


class PageMetaTag(BaseModel):
    id: Optional[str] = None
    """The ID of the Page Meta Tag."""

    value: Optional[str] = None
    """
    Locale-specific value of the Page Meta Tag, evaluated by resolving the rule set
    for the given Business Manager ID.
    """


class PriceRange(BaseModel):
    max_price: Optional[float] = FieldInfo(alias="maxPrice", default=None)
    """Document representing a price for a product"""

    min_price: Optional[float] = FieldInfo(alias="minPrice", default=None)
    """Document representing a price for a product"""

    pricebook: Optional[str] = None
    """The active pricebook from which the min and the max prices are calculated.

    The pricebook is based on the site context of the request as defined in ECOM.
    """


class ProductLink(BaseModel):
    source_product_id: str = FieldInfo(alias="sourceProductId")
    """The id (SKU) of the product."""

    source_product_link: str = FieldInfo(alias="sourceProductLink")
    """The URL addressing the product this product link is coming from."""

    target_product_id: str = FieldInfo(alias="targetProductId")
    """The id (SKU) of the product."""

    target_product_link: str = FieldInfo(alias="targetProductLink")
    """The URL addressing the product this product link is pointing to."""

    type: Literal[
        "cross_sell", "replacement", "up_sell", "accessory", "newer_version", "alt_orderunit", "spare_part", "other"
    ]
    """The type of product link."""


class ProductPromotion(BaseModel):
    callout_msg: str = FieldInfo(alias="calloutMsg")
    """The localized call-out message of the promotion."""

    promotional_price: float = FieldInfo(alias="promotionalPrice")
    """Document representing a price for a product"""

    promotion_id: str = FieldInfo(alias="promotionId")
    """The unique ID of the promotion."""


class RecommendationRecommendationType(BaseModel):
    display_value: str = FieldInfo(alias="displayValue")
    """The localized display value of the recommendation type."""

    value: int
    """The value of the recommendation type."""


class Recommendation(BaseModel):
    recommendation_type: RecommendationRecommendationType = FieldInfo(alias="recommendationType")
    """Document representing a recommendation type."""

    callout_msg: Optional[str] = FieldInfo(alias="calloutMsg", default=None)
    """The localized callout message of the recommendation."""

    image: Optional[Image] = None
    """Product image"""

    long_description: Optional[str] = FieldInfo(alias="longDescription", default=None)
    """The localized long description of the recommendation."""

    name: Optional[str] = None
    """The localized name of the recommendation."""

    recommended_item_id: Optional[str] = FieldInfo(alias="recommendedItemId", default=None)
    """The recommended item ID of the recommendation."""

    short_description: Optional[str] = FieldInfo(alias="shortDescription", default=None)
    """The localized short description of the recommendation."""


class Type(BaseModel):
    bundle: Optional[bool] = None
    """A flag indicating whether the product is a bundle."""

    item: Optional[bool] = None
    """A flag indicating whether the product is a standard item."""

    master: Optional[bool] = None
    """A flag indicating whether the product is a master."""

    option: Optional[bool] = None
    """A flag indicating whether the product is an option."""

    set: Optional[bool] = None
    """A flag indicating whether the product is a set."""

    variant: Optional[bool] = None
    """A flag indicating whether the product is a variant."""

    variation_group: Optional[bool] = FieldInfo(alias="variationGroup", default=None)
    """A flag indicating whether the product is a variation group."""


class Variant(BaseModel):
    product_id: str = FieldInfo(alias="productId")
    """The id (SKU) of the product."""

    orderable: Optional[bool] = None
    """A flag indicating whether the variant is orderable."""

    price: Optional[float] = None
    """Document representing a price for a product"""

    tiered_prices: Optional[List[ProductPriceTable]] = FieldInfo(alias="tieredPrices", default=None)
    """List of tiered prices if the product is a variant"""

    variation_values: Optional[Dict[str, str]] = FieldInfo(alias="variationValues", default=None)
    """The actual variation attribute ID - value pairs."""


class VariationGroup(BaseModel):
    orderable: bool
    """A flag indicating whether the variation group is orderable."""

    price: float
    """Document representing a price for a product"""

    product_id: str = FieldInfo(alias="productId")
    """The id (SKU) of the product."""

    variation_values: Dict[str, str] = FieldInfo(alias="variationValues")
    """The actual variation attribute ID - value pairs."""


class Product(BaseModel):
    id: str
    """The id (SKU) of the product."""

    brand: Optional[str] = None
    """The product's brand."""

    bundled_products: Optional[List["BundledProduct"]] = FieldInfo(alias="bundledProducts", default=None)
    """The array of all bundled products of this product."""

    currency: Union[str, Literal["N/A"], None] = None
    """
    A three letter uppercase currency code conforming to the
    [ISO 4217](https://www.iso.org/iso-4217-currency-codes.html) standard, or the
    string `N/A` indicating that a currency is not applicable.
    """

    ean: Optional[str] = None
    """The European Article Number of the product."""

    fetch_date: Optional[int] = FieldInfo(alias="fetchDate", default=None)

    image_groups: Optional[List[ImageGroup]] = FieldInfo(alias="imageGroups", default=None)
    """The array of product image groups."""

    inventories: Optional[List[Inventory]] = None
    """
    The array of product inventories explicitly requested via the 'inventory_ids'
    query parameter. This property is only returned in context of the 'availability'
    expansion.
    """

    inventory: Optional[Inventory] = None
    """
    Document representing inventory information of the current product for a
    particular inventory list.
    """

    long_description: Optional[str] = FieldInfo(alias="longDescription", default=None)
    """The localized product's long description."""

    manufacturer_name: Optional[str] = FieldInfo(alias="manufacturerName", default=None)
    """The product's manufacturer name."""

    manufacturer_sku: Optional[str] = FieldInfo(alias="manufacturerSku", default=None)
    """The product's manufacturer SKU."""

    master: Optional[Master] = None
    """The master product is a representation of a group of variant products.

    This is a non-buyable entity, provides inheritable attributes for its product
    variants, and is used for navigation. _Doesn't have a SKU._
    """

    min_order_quantity: Optional[float] = FieldInfo(alias="minOrderQuantity", default=None)
    """The minimum order quantity for this product."""

    name: Optional[str] = None
    """The localized product name."""

    options: Optional[List[Option]] = None
    """The array of product options, only for type option. This array can be empty."""

    page_description: Optional[str] = FieldInfo(alias="pageDescription", default=None)
    """The localized product's page description."""

    page_keywords: Optional[str] = FieldInfo(alias="pageKeywords", default=None)
    """The localized product's page description."""

    page_meta_tags: Optional[List[PageMetaTag]] = FieldInfo(alias="pageMetaTags", default=None)
    """Page Meta tags associated with the given product."""

    page_title: Optional[str] = FieldInfo(alias="pageTitle", default=None)
    """The localized product's page title."""

    price: Optional[float] = None
    """The sales price of the product.

    In case of complex products, like master or set, this is the minimum price of
    related child products.
    """

    price_max: Optional[float] = FieldInfo(alias="priceMax", default=None)
    """
    The maximum sales of related child products in complex products like master or
    set.
    """

    price_per_unit: Optional[float] = FieldInfo(alias="pricePerUnit", default=None)
    """The price per unit if defined for the product"""

    price_per_unit_max: Optional[float] = FieldInfo(alias="pricePerUnitMax", default=None)
    """The max price per unit typically for a master product's variant."""

    price_ranges: Optional[List[PriceRange]] = FieldInfo(alias="priceRanges", default=None)
    """
    Array of one or more price range objects representing one or more Pricebooks in
    context for the site.
    """

    prices: Optional[Dict[str, float]] = None
    """The prices map with pricebook IDs and their values."""

    primary_category_id: Optional[str] = FieldInfo(alias="primaryCategoryId", default=None)
    """The ID of the products primary category."""

    product_links: Optional[List[ProductLink]] = FieldInfo(alias="productLinks", default=None)
    """The array of source and target product links information."""

    product_promotions: Optional[List[ProductPromotion]] = FieldInfo(alias="productPromotions", default=None)
    """
    An array of active customer product promotions for this product, sorted by
    promotion priority using SORT_BY_EXCLUSIVITY ordering (exclusivity → rank →
    promotion class → discount type → best discount → ID). This array can be empty.
    Coupon promotions are not returned in this array. See
    [PromotionPlan.SORT_BY_EXCLUSIVITY](https://salesforcecommercecloud.github.io/b2c-dev-doc/docs/current/scriptapi/html/index.html?target=class_dw_campaign_PromotionPlan.html)
    for more details.
    """

    recommendations: Optional[List[Recommendation]] = None
    """Returns a list of recommendations."""

    set_products: Optional[List["Product"]] = FieldInfo(alias="setProducts", default=None)
    """The array of set products of this product."""

    short_description: Optional[str] = FieldInfo(alias="shortDescription", default=None)
    """The localized product short description."""

    slug_url: Optional[str] = FieldInfo(alias="slugUrl", default=None)
    """The complete link to this product's storefront page."""

    step_quantity: Optional[float] = FieldInfo(alias="stepQuantity", default=None)
    """The steps in which the order amount of the product can be increased."""

    tiered_prices: Optional[List[ProductPriceTable]] = FieldInfo(alias="tieredPrices", default=None)
    """The document represents list of tiered prices if the product is a variant"""

    type: Optional[Type] = None
    """Document representing a product type."""

    unit: Optional[str] = None
    """The sales unit of the product."""

    upc: Optional[str] = None
    """The Universal Product Code (UPC)."""

    valid_from: Optional[datetime] = FieldInfo(alias="validFrom", default=None)
    """The time a product is valid from."""

    valid_to: Optional[datetime] = FieldInfo(alias="validTo", default=None)
    """The time a product is valid to."""

    variants: Optional[List[Variant]] = None
    """The array of actual variants.

    Only for master, variation group, and variant types. This array can be empty.
    """

    variation_attributes: Optional[List[VariationAttribute]] = FieldInfo(alias="variationAttributes", default=None)
    """Sorted array of variation attributes information.

    Only for master, variation group, and variant types. This array can be empty.
    """

    variation_groups: Optional[List[VariationGroup]] = FieldInfo(alias="variationGroups", default=None)
    """The array of actual variation groups.

    Only for master, variation group, and variant types. This array can be empty.
    """

    variation_values: Optional[Dict[str, str]] = FieldInfo(alias="variationValues", default=None)
    """The actual variation attribute ID - value pairs.

    Only for variant and variation group types.
    """

    if TYPE_CHECKING:
        # Some versions of Pydantic <2.8.0 have a bug and don’t allow assigning a
        # value to this field, so for compatibility we avoid doing it at runtime.
        __pydantic_extra__: Dict[str, object] = FieldInfo(init=False)  # pyright: ignore[reportIncompatibleVariableOverride]

        # Stub to indicate that arbitrary properties are accepted.
        # To access properties that are not valid identifiers you can use `getattr`, e.g.
        # `getattr(obj, '$type')`
        def __getattr__(self, attr: str) -> object: ...
    else:
        __pydantic_extra__: Dict[str, object]


from .bundled_product import BundledProduct
