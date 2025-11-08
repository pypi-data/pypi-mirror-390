# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from pydantic import Field as FieldInfo

from .image import Image
from .._models import BaseModel

__all__ = ["VariationAttribute", "Value"]


class Value(BaseModel):
    value: str
    """
    The String4000 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 4000 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 4000
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      2000 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 1333 characters.
    """

    description: Optional[str] = None
    """
    The String4000 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 4000 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 4000
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      2000 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 1333 characters.
    """

    image: Optional[Image] = None
    """The first product image for the configured viewtype and this variation value."""

    image_swatch: Optional[Image] = FieldInfo(alias="imageSwatch", default=None)
    """The first product image for the configured viewtype and this variation value.

    Typically the swatch image.
    """

    name: Optional[str] = None
    """
    The String4000 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 4000 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 4000
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      2000 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 1333 characters.
    """

    orderable: Optional[bool] = None
    """
    A flag indicating whether at least one variant with this variation attribute
    value is available to sell.
    """


class VariationAttribute(BaseModel):
    id: str
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

    name: Optional[str] = None
    """
    The String4000 schema is a foundational schema designed for fields or attributes
    that are stored in a database field with a maximum capacity of 4000 bytes. This
    schema accommodates various character sets, with the following considerations:

    - ASCII Characters: Each ASCII character occupies 1 byte, allowing up to 4000
      characters.
    - Latin Characters: Many Latin characters require 2 bytes each, allowing up to
      2000 characters.
    - Asian Characters: Many Asian characters require 3 bytes each, allowing
      approximately 1333 characters.
    """

    values: Optional[List[Value]] = None
    """The sorted array of variation values. This array can be empty."""
