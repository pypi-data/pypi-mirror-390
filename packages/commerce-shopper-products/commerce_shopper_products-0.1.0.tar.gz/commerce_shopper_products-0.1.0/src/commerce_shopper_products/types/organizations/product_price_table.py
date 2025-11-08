# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from ..._models import BaseModel

__all__ = ["ProductPriceTable"]


class ProductPriceTable(BaseModel):
    price: Optional[float] = None
    """Document representing a price for a product"""

    pricebook: Optional[str] = None
    """The active pricebook for which this price is defined"""

    quantity: Optional[float] = None
    """Quantity tier for which the price is defined."""
