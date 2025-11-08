# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

from ..._models import BaseModel

__all__ = ["CategoryListResponse"]


class CategoryListResponse(BaseModel):
    data: List["Category"]
    """The array of category documents."""

    limit: int
    """Maximum records to retrieve per request, not to exceed the maximum defined.

    A limit must be at least 1 so at least one record is returned (if any match the
    criteria).
    """

    total: int
    """The total number of hits that match the search's criteria.

    This can be greater than the number of results returned as search results are
    pagenated.
    """


from .category import Category
