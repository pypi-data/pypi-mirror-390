import functools

from .base_classes import Container, Void


class BaseURL(Void):
    """The HTML `<base>` element specifies the base URL to use for *all*
    relative URLs in a document. There can be only one `<base>` element in a
    document.
    """

    __slots__ = ()
    tag = "base"


Base = BaseURL


class ExternalResourceLink(Void):
    """The HTML External Resource Link element (`<link>`) specifies
    relationships between the current document and an external resource.
    This element is most commonly used to link to stylesheets, but is
    also used to establish site icons (both "favicon" style icons and
    icons for the home screen and apps on mobile devices) among other
    things.
    """

    __slots__ = ()
    tag = "link"


Link = ExternalResourceLink

ExternalStyleSheet = functools.partial(ExternalResourceLink, rel="stylesheet")


class Meta(Void):
    """The HTML `<meta>` element represents metadata that cannot be
    represented by other HTML meta-related elements, like `<base>`,
    `<link>`, `<script>`, `<style>` or `<title>`.
    """

    __slots__ = ()
    tag = "meta"


class Style(Container):
    """The HTML `<style>` element contains style information for a
    document, or part of a document.
    """

    __slots__ = ()
    tag = "style"


class Title(Container):
    """The HTML Title element (`<title>`) defines the document's title
    that is shown in a browser's title bar or a page's tab.
    """

    __slots__ = ()
    tag = "title"
