# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .image import Image
from ..._models import BaseModel

__all__ = ["VariationAttributeValue"]


class VariationAttributeValue(BaseModel):
    value: str
    """The actual variation value."""

    description: Optional[str] = None
    """The localized description of the variation value."""

    image: Optional[Image] = None
    """Product image"""

    image_swatch: Optional[Image] = FieldInfo(alias="imageSwatch", default=None)
    """Product image"""

    name: Optional[str] = None
    """The localized display name of the variation value."""

    orderable: Optional[bool] = None
    """
    A flag indicating whether at least one variant with this variation attribute
    value is available to sell.
    """
