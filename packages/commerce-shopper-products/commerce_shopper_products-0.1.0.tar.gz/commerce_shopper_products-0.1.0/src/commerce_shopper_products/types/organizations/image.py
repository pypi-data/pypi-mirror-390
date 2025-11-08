# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Image"]


class Image(BaseModel):
    link: str
    """The URL of the actual image."""

    alt: Optional[str] = None
    """The localized alternative text of the image."""

    dis_base_link: Optional[str] = FieldInfo(alias="disBaseLink", default=None)
    """Base URL for the Dynamic Image Service (DIS) address.

    This is only shown if the image is stored on the server and DIS is enabled.
    """

    title: Optional[str] = None
    """The localized title of the image."""
