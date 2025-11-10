import json
import typing
from abc import ABCMeta, abstractmethod
from textwrap import indent

Attributes = typing.Dict[str, typing.Any]
Content = typing.List[typing.Union["Element", str]]


def transform(attributes: Attributes) -> typing.Dict[str, str]:
    """Transform `attributes` for serialisation.

    `attributes` is not mutated aside from style and class normalisation;
    a new dictionary is returned to be serialised.

    `classes`, if present, must be a `set` of classes to apply to the
    element. Empty strings will be removed from this set, so they are
    useable to toggle a class with a boolean.

    `style`, if present, must be either a dictionary of CSS properties to their
    values, or a string. If it is a dictionary, it will be auto-serialised to
    minified CSS.

    Any attribute name with an underscore in it has its underscores
    transformed into hyphens (for ARIA, JavaScript `data-` attributes,
    and similar) - use two underscores to represent a literal underscore.

    Additionally, single trailing underscores are removed.

    Attribute values are serialised as JSON, and non-strings are then
    serialised as JSON again (to be XHTML-compliant and avoid breaking
    arrays or objects as attribute values).
    """
    new_attributes = {}
    classes = attributes.pop("classes", set())
    if classes:
        attributes["class"] = " ".join(classes - {""})
    style = attributes.pop("style", "")
    if style:
        if isinstance(style, dict):
            style = ";".join(key + ":" + value for key, value in style.items())
        attributes["style"] = style
    for key, value in attributes.items():
        # if both `*colour*` and `*color*` are provided, `*colour*` takes
        # precedence
        unnormalised_colour = (
            key if key.startswith("data-") else key.replace("color", "colour")
        )
        if key != unnormalised_colour and unnormalised_colour in attributes:
            continue
        if not isinstance(value, str):
            # convert value to a string containing JSON
            value = json.dumps(value)
        # convert value to a JSON-encoded string (double quotes, for HTML
        # attribute values)
        value = json.dumps(value.replace('"', "&quot;"))
        # remove single trailing underscore
        if key[-1] == "_" and key[-2] != "_":
            key = key[:-1]
        # replace double underscore with single underscore, and other
        # underscores with hyphens
        key = key.replace("__", " ").replace("_", "-").replace(" ", "_")
        # allow global use of `colour` instead of `color`, but don't modify
        # `data-*` attributes
        if not key.startswith("data-"):
            key = key.replace("colour", "color")
        new_attributes[key] = value
    return new_attributes


class Element(metaclass=ABCMeta):
    """Base class for all elements

    You should never need to inherit from this directly - use `Component` in
    most cases, or for custom elements use `Container` and `Void`

    When any element is created, its `apply_attributes` method is guaranteed
    to be called first, followed by its `set_content` method.

    Note: If the element is then called (HTML-style content initialisation)
    then its `set_content` method will be called again
    """

    __slots__ = ()

    def __init__(
        self, *content: typing.Union["Element", str], **attributes: typing.Any
    ) -> None:
        self.apply_attributes(attributes)
        self.set_content(list(content))

    def __call__(self, *content: typing.Union["Element", str]) -> "Element":
        self.set_content(list(content))
        return self

    @abstractmethod
    def serialise(self, minify: bool = True) -> str:
        """Return an HTML representation of the model"""

    @abstractmethod
    def set_content(self, content: Content) -> None:
        """Set content - called by __init__ and __call__"""

    @abstractmethod
    def apply_attributes(self, attributes: Attributes) -> None:
        """Apply attributes - called by __init__

        Guaranteed to be called before set_content"""

    def __str__(self) -> str:
        return self.serialise(minify=False)


class TextElement(Element):
    __slots__ = ("content",)
    content: str

    def serialise(self, minify: bool = True) -> str:
        """Return an HTML representation of the model"""
        return self.content

    def set_content(self, content: Content) -> None:
        if not isinstance(content[0], str):
            raise TypeError(
                "Text content must be a single string (got {!r})".format(
                    type(self.content).__qualname__
                )
            )
        if len(content) != 1:
            raise TypeError(
                "Text content must be a single string (got {} items)".format(
                    len(content)
                )
            )
        self.content = content[0]

    def apply_attributes(self, attributes: Attributes) -> None:
        if attributes:
            raise TypeError("Text content cannot have attributes")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.content!r})"


class Container(Element):
    """Base class for all container/non-void elements

    Most inheriters only need to define `tag`
    """

    __slots__ = ("tag", "content", "attributes")
    tag: str
    content: typing.List["Element"]
    attributes: Attributes

    def serialise(self, minify: bool = True) -> str:
        """Return an HTML representation of the model"""
        return (
            "<"
            + self.tag
            + (
                (" " + " ".join(f"{k}={v}" for k, v in self.attributes.items()))
                if self.attributes
                else ""
            )
            + ">"
            + ("" if minify else "\n")
            + indent(
                ("" if minify else "\n").join(
                    child.serialise(minify=minify) for child in self.content
                ),
                "    ",
                lambda _: not minify,
            )
            + ("" if minify else "\n")
            + f"</{self.tag}>"
        )

    def set_content(self, content: Content) -> None:
        self.content = [
            child if isinstance(child, Element) else TextElement(child)
            for child in content
        ]

    def apply_attributes(self, attributes: Attributes) -> None:
        self.attributes = transform(attributes)

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "("
            + ", ".join(repr(child) for child in self.content)
            + (", " if self.content and self.attributes else "")
            # our attribute values are already quoted
            + ", ".join(f"{k}={v}" for k, v in self.attributes.items())
            + ")"
        )


class Void(Element):
    """Base class for all non-container/void elements

    Most inheriters only need to define `tag`
    """

    __slots__ = ("tag", "attributes")
    tag: str
    attributes: Attributes

    def serialise(self, minify: bool = True) -> str:
        """Return an HTML representation of the model"""
        return (
            "<"
            + self.tag
            + (
                (" " + " ".join(f"{k}={v}" for k, v in self.attributes.items()))
                if self.attributes
                else ""
            )
            + " />"
        )

    def set_content(self, content: Content) -> None:
        if content:
            raise TypeError("Void elements cannot have content")

    def apply_attributes(self, attributes: Attributes) -> None:
        self.attributes = transform(attributes)

    def __repr__(self) -> str:
        return (
            self.__class__.__name__
            + "("
            # our attribute values are already quoted
            + ", ".join(f"{k}={v}" for k, v in self.attributes.items())
            + ")"
        )


class ElementGroup(Element):
    """A group of elements. Useful for creating Components"""

    __slots__ = ("content",)
    content: typing.List[Element]

    def set_content(self, content: Content) -> None:
        self.content = [
            child if isinstance(child, Element) else TextElement(child)
            for child in content
        ]

    def apply_attributes(self, attributes: Attributes) -> None:
        if attributes:
            raise TypeError("Element groups cannot have attributes")

    def serialise(self, minify: bool = True) -> str:
        return ("" if minify else "\n").join(
            child.serialise(minify=minify) for child in self.content
        )


class Component(Element):
    """Base class for custom components

    `apply_attributes` is always called before `set_content` so it can be
    used to control the behaviour of the component
    """

    __slots__ = ("content",)
    content: Element

    def serialise(self, minify: bool = True) -> str:
        """Return an HTML representation of the model"""
        return self.content.serialise(minify=minify)
