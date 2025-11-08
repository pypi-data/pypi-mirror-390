# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

from ..._models import BaseModel

__all__ = ["ProductListResponse"]


class ProductListResponse(BaseModel):
    data: List["Product"]
    """The array of product documents."""

    limit: int
    """The number of returned documents."""

    total: int
    """The total number of documents."""


from .product import Product
