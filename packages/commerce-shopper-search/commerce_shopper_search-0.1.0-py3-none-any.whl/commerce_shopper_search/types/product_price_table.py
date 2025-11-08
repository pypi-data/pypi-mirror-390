# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["ProductPriceTable"]


class ProductPriceTable(BaseModel):
    price: Optional[float] = None
    """Price for the product for the specified tier for the specified pricebook"""

    pricebook: Optional[str] = None
    """
    The String256 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 256 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 256
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      128 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 85 characters.
    """

    quantity: Optional[float] = None
    """Quantity tier for which the price is defined."""
