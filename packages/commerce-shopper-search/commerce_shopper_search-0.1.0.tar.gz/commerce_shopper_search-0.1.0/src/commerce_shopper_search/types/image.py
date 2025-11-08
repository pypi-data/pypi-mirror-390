# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["Image"]


class Image(BaseModel):
    link: str
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

    alt: Optional[str] = None
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

    dis_base_link: Optional[str] = FieldInfo(alias="disBaseLink", default=None)
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

    title: Optional[str] = None
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
