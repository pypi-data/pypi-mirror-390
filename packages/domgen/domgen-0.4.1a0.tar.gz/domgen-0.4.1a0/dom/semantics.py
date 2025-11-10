import typing

from .base_classes import Container, Element, TextElement, Void


class Anchor(Container):
    """The HTML/SVG `<a>` element (or anchor element), with its `href`
    attribute, creates a hyperlink to web pages, files, email addresses,
    locations in the same page, or anything else a URL can address.
    """

    __slots__ = ()
    tag = "a"


A = Anchor


class Abbreviation(Container):
    """The HTML Abbreviation element (`<abbr>`) represents an abbreviation
    or acronym; the optional `title` attribute can provide an expansion or
    description for the abbreviation.
    """

    __slots__ = ()
    tag = "abbr"


Abbr = Abbreviation


class BringAttentionTo(Container):
    """The HTML Bring Attention To element (`<b>`) is used to draw the
    reader's attention to the element's contents, which are not otherwise
    granted special importance.
    """

    __slots__ = ()
    tag = "b"


B = BringAttentionTo


class BidirectionalIsolateElement(Container):
    """The HTML Bidirectional Isolate element (`<bdi>`) tells the browser's
    bidirectional algorithm to treat the text it contains in isolation
    from its surrounding text.
    """

    __slots__ = ()
    tag = "bdi"


BDI = BidirectionalIsolateElement


class BidirectionalTextOverride(Container):
    """The HTML Bidirectional Text Override element (`<bdo>`) overrides the
    current directionality of text, so that the text within is rendered in a
    different direction.
    """

    __slots__ = ()
    tag = "bdo"


BDO = BidirectionalTextOverride


class LineBreak(Void):
    """The HTML `<br>` element produces a line break in text (carriage-return).
    It is useful for writing a poem or an address, where the division of lines
    is significant.
    """

    __slots__ = ()
    tag = "br"


Br = LineBreak


class Citation(Container):
    """The HTML Citation element (`<cite>`) is used to describe a reference
    to a cited creative work, and must include the title of that work.
    """

    __slots__ = ()
    tag = "cite"


Cite = Citation


class Code(Container):
    """The HTML `<code>` element displays its contents styled in a fashion
    intended to indicate that the text is a short fragment of computer code.
    """

    __slots__ = ()
    tag = "code"


class Data(Container):
    """The HTML `<data>` element links a given piece of content with a
    machine-readable translation. If the content is time- or date-related,
    the `<time>` element must be used.

    Example:
    ```html
    <p>New Products</p>
    <ul>
        <li><data value="398">Mini Ketchup</data></li>
        <li><data value="399">Jumbo Ketchup</data></li>
        <li><data value="400">Mega Jumbo Ketchup</data></li>
    </ul>
    ```
    """

    __slots__ = ()
    tag = "data"


class Definition(Container):
    """The HTML Definition element (`<dfn>`) is used to indicate the term
    being defined within the context of a definition phrase or sentence.
    """

    __slots__ = ()
    tag = "dfn"


Dfn = Definition


class Emphasis(Container):
    """The HTML `<em>` element marks text that has stress emphasis. The
    `<em>` element can be nested, with each level of nesting indicating a
    greater degree of emphasis.
    """

    __slots__ = ()
    tag = "em"


Em = Emphasis


class IdiomaticText(Container):
    """The HTML Idiomatic Text element (`<i>`) represents a range of text
    that is set off from the normal text for some reason, such as idiomatic
    text, technical terms, taxonomical designations, among others.
    """

    __slots__ = ()
    tag = "i"


I = IdiomaticText


class KeyboardInput(Container):
    """The HTML Keyboard Input element (`<kbd>`) represents a span of inline
    text denoting textual user input from a keyboard, voice input, or any
    other text entry device.
    """

    __slots__ = ()
    tag = "kbd"


Kbd = KeyboardInput


class MarkText(Container):
    """The HTML Mark Text element (`<mark>`) represents text which is marked
    or highlighted for reference or notation purposes, due to the marked
    passage's relevance or importance in the enclosing context.
    """

    __slots__ = ()
    tag = "mark"


Mark = MarkText


class InlineQuotation(Container):
    """The HTML `<q>` element indicates that the enclosed text is a short
    inline quotation. Most modern browsers implement this by surrounding
    the text in quotation marks.
    """

    __slots__ = ()
    tag = "q"


Q = InlineQuotation


class RubyText(Container):
    """The HTML Ruby Text (`<rt>`) element specifies the ruby text component
    of a ruby annotation, which is used to provide pronunciation, translation,
    or transliteration information for East Asian typography. The `<rt>`
    element must always be contained within a `<ruby>` element.
    """

    __slots__ = ()
    tag = "rt"


RT = RubyText


class RubyFallback(Container):
    """The HTML Ruby Fallback Parenthesis (`<rp>`) element is used to provide
    fall-back parentheses for browsers that do not support display of ruby
    annotations using the `<ruby>` element.
    """

    __slots__ = ()
    tag = "rp"


RP = RubyFallback


class Ruby(Container):
    """The HTML `<ruby>` element represents small annotations that are
    rendered above, below, or next to base text, usually used for showing
    the pronunciation of East Asian characters. It can also be used for
    annotating other kinds of text, but this usage is less common.
    """

    __slots__ = ()
    tag = "ruby"


class Strikethrough(Container):
    """The HTML `<s>` element renders text with a strikethrough, or a line
    through it. Use the `<s>` element to represent things that are no longer
    relevant or no longer accurate. However, `<s>` is not appropriate when
    indicating document edits; for that, use the `<del>` and `<ins>` elements,
    as appropriate.
    """

    __slots__ = ()
    tag = "s"


S = Strikethrough


class SampleOutput(Container):
    """The HTML Sample Element (`<samp>`) is used to enclose inline text which
    represents sample (or quoted) output from a computer program.
    """

    __slots__ = ()
    tag = "samp"


Samp = SampleOutput


class Small(Container):
    """The HTML `<small>` element represents side-comments and small print,
    like copyright and legal text, independent of its styled presentation. By
    default, it renders text within it one font-size smaller, such as from
    small to x-small.
    """

    __slots__ = ()
    tag = "small"


class Span(Container):
    """The HTML `<span>` element is a generic inline container for phrasing
    content, which does not inherently represent anything. It can be used to
    group elements for styling purposes (using the `class` or `id` attributes),
    or because they share attribute values, such as `lang`.
    """

    __slots__ = ()
    tag = "span"


class StrongImportance(Container):
    """The HTML Strong Importance Element (`<strong>`) indicates that its
    contents have strong importance, seriousness, or urgency. Browsers
    typically render the contents in bold type.
    """

    __slots__ = ()
    tag = "strong"


Strong = StrongImportance


class Subscript(Container):
    """The HTML Subscript element (`<sub>`) specifies inline text which
    should be displayed as subscript for solely typographical reasons.
    """

    __slots__ = ()
    tag = "sub"


Sub = Subscript


class Superscript(Container):
    """The HTML Superscript element (`<sup>`) specifies inline text which
    is to be displayed as superscript for solely typographical reasons.
    """

    __slots__ = ()
    tag = "sup"


Sup = Superscript


class Time(Container):
    """The HTML <time> element represents a specific period in time.

    ```html
    <time datetime="2018-07-07">7th July</time>
    <time datetime="20:00">20:00</time>
    <time datetime="PT2H30M">2h30m</time>
    ```

    ## Valid datetime Values

    - a valid year string
        - `2011`
    - a valid month string
        - `2011-11`
    - a valid date string
        - `2011-11-18`
    - a valid yearless date string
        - `11-18`
    - a valid week string
        - `2011-W47`
    - a valid time string
        - `14:54`
    14:54:39
    14:54:39.929
    - a valid local date and time string
        - `2011-11-18T14:54:39.929`
    2011-11-18 14:54:39.929
    - a valid global date and time string
        - `2011-11-18T14:54:39.929Z`
        - `2011-11-18T14:54:39.929-0400`
        - `2011-11-18T14:54:39.929-04:00`
        - `2011-11-18 14:54:39.929Z`
        - `2011-11-18 14:54:39.929-0400`
        - `2011-11-18 14:54:39.929-04:00`
    - a valid duration string
        - `PT4H18M3S`
    """

    __slots__ = ()
    tag = "time"


class UnarticulatedAnnotation(Container):
    """The HTML Unarticulated Annotation element (`<u>`) represents a span of
    inline text which should be rendered in a way that indicates that it has a
    non-textual annotation.
    """

    __slots__ = ()
    tag = "u"


U = UnarticulatedAnnotation


class Variable(Container):
    """The HTML Variable element (`<var>`) represents the name of a variable
    in a mathematical expression or a programming context.
    """

    __slots__ = ()
    tag = "var"


Var = Variable


class WordBreak(Void):
    """The HTML `<wbr>` element represents a word break opportunity — a
    position within text where the browser may optionally break a line, though
    its line-breaking rules would not otherwise create a break at that
    location.
    """

    __slots__ = ()
    tag = "wbr"


WBr = WordBreak


class DeletedText(Container):
    """The HTML `<del>` element represents a range of text that has been
    deleted from a document.
    """

    __slots__ = ()
    tag = "del"


Del = DeletedText


class InsertedText(Container):
    """The HTML `<ins>` element represents a range of text that has been
    added to a document.
    """

    __slots__ = ()
    tag = "ins"


Ins = InsertedText
