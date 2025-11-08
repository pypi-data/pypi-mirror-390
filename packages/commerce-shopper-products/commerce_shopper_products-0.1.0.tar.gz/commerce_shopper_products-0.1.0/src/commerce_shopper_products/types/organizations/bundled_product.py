# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from ..._models import BaseModel

__all__ = ["BundledProduct"]


class BundledProduct(BaseModel):
    id: str

    product: "Product"
    """
    Any product that is sold, shown alone, and does not have variations such as
    different sizes or colors. A product has no reliance on any other product for
    inheritance. _A product has a SKU and can have a product option, which has a
    different SKU_.
    """

    quantity: float
    """For the product being bundled, the quantity added to the bundle."""


from .product import Product
