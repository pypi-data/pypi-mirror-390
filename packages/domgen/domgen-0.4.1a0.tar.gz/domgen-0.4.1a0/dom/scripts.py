from .base_classes import Container


class Canvas(Container):
    """Use the HTML `<canvas>` element with either the [canvas scripting
    API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API) or the
    [WebGL API](https://developer.mozilla.org/en-US/docs/Web/API/WebGL_API) to
    draw graphics and animations.

    You may (and should) provide alternate content inside the `<canvas>`
    block. That content will be rendered both on older browsers that don't
    support canvas and in browsers with JavaScript disabled. Providing a
    useful fallback text or sub DOM helps to make the the canvas more
    accessible.
    """

    __slots__ = ()
    tag = "canvas"


class NoScript(Container):
    """The HTML `<noscript>` element defines a section of HTML to be inserted
    if a script type on the page is unsupported or if scripting is currently
    turned off in the browser.
    """

    __slots__ = ()
    tag = "noscript"


class Script(Container):
    """The HTML `<script>` element is used to embed executable code or data;
    this is typically used to embed or refer to JavaScript code.

    When used in SVG, `href` should be used instead of `src`.
    """

    __slots__ = ()
    tag = "script"
