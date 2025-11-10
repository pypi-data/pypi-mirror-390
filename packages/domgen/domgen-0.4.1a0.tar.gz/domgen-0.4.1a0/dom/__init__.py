import typing

from . import (
    base_classes,
    components,
    content,
    forms,
    interactive_elements,
    media,
    metadata,
    scripts,
    sectioning,
    semantics,
    short,
    svg,
    tables,
)
from .plain_elements import *
from .short import *


def custom(
    tag_name: str,
    void: bool = True,
) -> typing.Type[Element]:
    """Create an ad-hoc Element class. Good for using web components."""
    if void:

        class CustomVoid(Void):
            tag = tag_name

            def __repr__(self) -> str:
                return (
                    "custom("
                    + repr(self.tag)
                    + ")("
                    + ", ".join(f"{k}={v}" for k, v in self.attributes.items())
                    + ")"
                )

        return CustomVoid
    else:

        class CustomContainer(Container):
            tag = tag_name

            def __repr__(self) -> str:
                return (
                    "custom("
                    + repr(self.tag)
                    + ")("
                    + ", ".join(repr(child) for child in self.content)
                    + (", " if self.content and self.attributes else "")
                    + ", ".join(f"{k}={v!r}" for k, v in self.attributes.items())
                    + ")"
                )

        return CustomContainer


__version__ = "0.4.1a"
