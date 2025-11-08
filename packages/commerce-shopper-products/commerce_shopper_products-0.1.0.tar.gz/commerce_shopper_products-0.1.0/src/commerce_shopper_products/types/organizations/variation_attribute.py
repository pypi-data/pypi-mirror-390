# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from ..._models import BaseModel
from .variation_attribute_value import VariationAttributeValue

__all__ = ["VariationAttribute"]


class VariationAttribute(BaseModel):
    id: str
    """The ID of the variation attribute."""

    name: Optional[str] = None
    """The localized display name of the variation attribute."""

    values: Optional[List[VariationAttributeValue]] = None
    """The sorted array of variation values. This array can be empty."""
