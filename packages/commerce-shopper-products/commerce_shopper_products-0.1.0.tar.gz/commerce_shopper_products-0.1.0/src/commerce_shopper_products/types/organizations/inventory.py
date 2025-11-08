# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Inventory"]


class Inventory(BaseModel):
    id: str
    """The inventory ID."""

    ats: Optional[float] = None
    """The Available To Sell (ATS) of the product.

    If it is infinity, the return value is 999999. The value can be overwritten by
    the OCAPI setting 'product.inventory.ats.max_threshold'.
    """

    backorderable: Optional[bool] = None
    """A flag indicating whether the product is backorderable."""

    in_stock_date: Optional[datetime] = FieldInfo(alias="inStockDate", default=None)
    """A flag indicating the date when the product will be in stock."""

    orderable: Optional[bool] = None
    """A flag indicating whether at least one of the products is available to sell."""

    preorderable: Optional[bool] = None
    """A flag indicating whether the product is preorderable."""

    stock_level: Optional[float] = FieldInfo(alias="stockLevel", default=None)
    """The stock level of the product.

    If it is infinity, the return value is 999999. The value can be overwritten by
    the OCAPI setting 'product.inventory.stock_level.max_threshold'.
    """
