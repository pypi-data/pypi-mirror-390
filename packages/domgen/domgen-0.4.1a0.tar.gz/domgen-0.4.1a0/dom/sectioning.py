from .base_classes import Container


class ContactAddress(Container):
    """The HTML `<address>` element indicates that the enclosed HTML
    provides contact information for a person or people, or for an
    organisation.
    """

    __slots__ = ()
    tag = "address"


Address = ContactAddress


class ArticleContents(Container):
    """The HTML `<article>` element represents a self-contained
    composition in a document, page, application, or site, which is
    intended to be independently distributable or reusable (e.g.,
    in syndication).
    """

    __slots__ = ()
    tag = "article"


Article = ArticleContents


class Aside(Container):
    """The HTML `<aside>` element represents a portion of a document
    whose content is only indirectly related to the document's main
    content.
    """

    __slots__ = ()
    tag = "aside"


class Footer(Container):
    """The HTML `<footer>` element represents a footer for its nearest
    sectioning content or sectioning root element. A footer typically
    contains information about the author of the section, copyright
    data or links to related documents.
    """

    __slots__ = ()
    tag = "footer"


class Header(Container):
    """The HTML `<header>` element represents introductory content,
    typically a group of introductory or navigational aids. It may
    contain some heading elements but also a logo, a search form, an
    author name, and other elements.
    """

    __slots__ = ()
    tag = "header"


class Heading1(Container):
    """The HTML `<h1>`–`<h6>` elements represent six levels of section
    headings. `<h1>` is the highest section level and `<h6>` is the
    lowest.
    """

    __slots__ = ()
    tag = "h1"


class Heading2(Container):
    """The HTML `<h1>`–`<h6>` elements represent six levels of section
    headings. `<h1>` is the highest section level and `<h6>` is the
    lowest.
    """

    __slots__ = ()
    tag = "h2"


class Heading3(Container):
    """The HTML `<h1>`–`<h6>` elements represent six levels of section
    headings. `<h1>` is the highest section level and `<h6>` is the
    lowest.
    """

    __slots__ = ()
    tag = "h3"


class Heading4(Container):
    """The HTML `<h1>`–`<h6>` elements represent six levels of section
    headings. `<h1>` is the highest section level and `<h6>` is the
    lowest.
    """

    __slots__ = ()
    tag = "h4"


class Heading5(Container):
    """The HTML `<h1>`–`<h6>` elements represent six levels of section
    headings. `<h1>` is the highest section level and `<h6>` is the
    lowest.
    """

    __slots__ = ()
    tag = "h5"


class Heading6(Container):
    """The HTML `<h1>`–`<h6>` elements represent six levels of section
    headings. `<h1>` is the highest section level and `<h6>` is the
    lowest.
    """

    __slots__ = ()
    tag = "h6"


H1 = Heading1
H2 = Heading2
H3 = Heading3
H4 = Heading4
H5 = Heading5
H6 = Heading6


class HeadingGroup(Container):
    """The HTML `<hgroup>` element represents a multi-level heading for
    a section of a document. It groups a set of `<h1>`–`<h6>` elements.
    """

    __slots__ = ()
    tag = "hgroup"


HGroup = HeadingGroup


class MainContent(Container):
    """The HTML `<main>` element represents the dominant content of the
    `<body>` of a document. The main content area consists of content
    that is directly related to or expands upon the central topic of a
    document, or the central functionality of an application.
    """

    __slots__ = ()
    tag = "main"


Main = MainContent


class Navigation(Container):
    """The HTML `<nav>` element represents a section of a page whose
    purpose is to provide navigation links, either within the current
    document or to other documents. Common examples of navigation
    sections are menus, tables of contents, and indexes.
    """

    __slots__ = ()
    tag = "nav"


Nav = Navigation


class Section(Container):
    """The HTML `<section>` element represents a standalone section -
    which doesn't have a more specific semantic element to represent it
    - contained within an HTML document.
    """

    __slots__ = ()
    tag = "section"


class HTML(Container):
    """The HTML `<html>` element represents the root (top-level element)
    of an HTML document, so it is also referred to as the root element.
    All other elements must be descendants of this element.
    """

    __slots__ = ()
    tag = "html"

    def serialise(self, minify: bool = True) -> str:
        return (
            "<!DOCTYPE html>"
            + ("" if minify else "\n")
            + super().serialise(minify=minify)
        )


class Head(Container):
    """The HTML `<head>` element contains machine-readable information
    (metadata) about the document, like its title, scripts, and style
    sheets.
    """

    __slots__ = ()
    tag = "head"


class Body(Container):
    """The HTML `<body>` Element represents the content of an HTML document.
    There can be only one `<body>` element in a document.
    """

    __slots__ = ()
    tag = "body"
