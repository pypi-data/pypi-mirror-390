# Organizations

Types:

```python
from commerce_shopper_search.types import (
    CurrencyCode,
    Image,
    ProductPriceTable,
    ProductPromotion,
    ProductRef,
    ProductSearchRefinementValue,
    SuggestedPhrase,
    SuggestedTerms,
    Suggestion,
    VariationAttribute,
    OrganizationProductSearchResponse,
    OrganizationSearchSuggestionsResponse,
)
```

Methods:

- <code title="get /organizations/{organizationId}/product-search">client.organizations.<a href="./src/commerce_shopper_search/resources/organizations.py">product_search</a>(organization_id, \*\*<a href="src/commerce_shopper_search/types/organization_product_search_params.py">params</a>) -> <a href="./src/commerce_shopper_search/types/organization_product_search_response.py">OrganizationProductSearchResponse</a></code>
- <code title="get /organizations/{organizationId}/search-suggestions">client.organizations.<a href="./src/commerce_shopper_search/resources/organizations.py">search_suggestions</a>(organization_id, \*\*<a href="src/commerce_shopper_search/types/organization_search_suggestions_params.py">params</a>) -> <a href="./src/commerce_shopper_search/types/organization_search_suggestions_response.py">OrganizationSearchSuggestionsResponse</a></code>
