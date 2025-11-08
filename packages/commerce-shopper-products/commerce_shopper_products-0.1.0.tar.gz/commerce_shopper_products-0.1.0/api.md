# Organizations

## Products

Types:

```python
from commerce_shopper_products.types.organizations import (
    BundledProduct,
    Category,
    Image,
    Inventory,
    Product,
    ProductPriceTable,
    VariationAttribute,
    VariationAttributeValue,
    ProductListResponse,
)
```

Methods:

- <code title="get /organizations/{organizationId}/products/{id}">client.organizations.products.<a href="./src/commerce_shopper_products/resources/organizations/products.py">retrieve</a>(id, \*, organization_id, \*\*<a href="src/commerce_shopper_products/types/organizations/product_retrieve_params.py">params</a>) -> <a href="./src/commerce_shopper_products/types/organizations/product.py">Product</a></code>
- <code title="get /organizations/{organizationId}/products">client.organizations.products.<a href="./src/commerce_shopper_products/resources/organizations/products.py">list</a>(organization_id, \*\*<a href="src/commerce_shopper_products/types/organizations/product_list_params.py">params</a>) -> <a href="./src/commerce_shopper_products/types/organizations/product_list_response.py">ProductListResponse</a></code>

## Categories

Types:

```python
from commerce_shopper_products.types.organizations import CategoryListResponse
```

Methods:

- <code title="get /organizations/{organizationId}/categories/{id}">client.organizations.categories.<a href="./src/commerce_shopper_products/resources/organizations/categories.py">retrieve</a>(id, \*, organization_id, \*\*<a href="src/commerce_shopper_products/types/organizations/category_retrieve_params.py">params</a>) -> <a href="./src/commerce_shopper_products/types/organizations/category.py">Category</a></code>
- <code title="get /organizations/{organizationId}/categories">client.organizations.categories.<a href="./src/commerce_shopper_products/resources/organizations/categories.py">list</a>(organization_id, \*\*<a href="src/commerce_shopper_products/types/organizations/category_list_params.py">params</a>) -> <a href="./src/commerce_shopper_products/types/organizations/category_list_response.py">CategoryListResponse</a></code>
