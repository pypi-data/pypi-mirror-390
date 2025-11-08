# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from . import organizations
from .. import _compat

# Rebuild cyclical models only after all modules are imported.
# This ensures that, when building the deferred (due to cyclical references) model schema,
# Pydantic can resolve the necessary references.
# See: https://github.com/pydantic/pydantic/issues/11250 for more context.
if _compat.PYDANTIC_V1:
    organizations.bundled_product.BundledProduct.update_forward_refs()  # type: ignore
    organizations.category.Category.update_forward_refs()  # type: ignore
    organizations.product.Product.update_forward_refs()  # type: ignore
    organizations.product_list_response.ProductListResponse.update_forward_refs()  # type: ignore
    organizations.category_list_response.CategoryListResponse.update_forward_refs()  # type: ignore
else:
    organizations.bundled_product.BundledProduct.model_rebuild(_parent_namespace_depth=0)
    organizations.category.Category.model_rebuild(_parent_namespace_depth=0)
    organizations.product.Product.model_rebuild(_parent_namespace_depth=0)
    organizations.product_list_response.ProductListResponse.model_rebuild(_parent_namespace_depth=0)
    organizations.category_list_response.CategoryListResponse.model_rebuild(_parent_namespace_depth=0)
