# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import TYPE_CHECKING, Dict, List, Optional

from pydantic import Field as FieldInfo

from ..._models import BaseModel

__all__ = ["Category", "ParentCategoryTree"]


class ParentCategoryTree(BaseModel):
    id: Optional[str] = None
    """The id of the category path."""

    name: Optional[str] = None
    """The name of the category path."""


class Category(BaseModel):
    id: str
    """The ID of the category."""

    categories: Optional[List["Category"]] = None
    """Array of subcategories. Can be empty."""

    description: Optional[str] = None
    """The localized description of the category."""

    image: Optional[str] = None
    """The URL of the category image."""

    name: Optional[str] = None
    """The localized name of the category."""

    online_sub_categories_count: Optional[int] = FieldInfo(alias="onlineSubCategoriesCount", default=None)
    """The total number of online sub-categories.

    This information will be available from B2C Commerce version 24.5.
    """

    page_description: Optional[str] = FieldInfo(alias="pageDescription", default=None)
    """The localized page description of the category."""

    page_keywords: Optional[str] = FieldInfo(alias="pageKeywords", default=None)
    """The localized page keywords of the category."""

    page_title: Optional[str] = FieldInfo(alias="pageTitle", default=None)
    """The localized page title of the category."""

    parent_category_id: Optional[str] = FieldInfo(alias="parentCategoryId", default=None)
    """The ID of the parent category."""

    parent_category_tree: Optional[List[ParentCategoryTree]] = FieldInfo(alias="parentCategoryTree", default=None)
    """The List of the parent categories."""

    thumbnail: Optional[str] = None
    """The URL of the category thumbnail."""

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
