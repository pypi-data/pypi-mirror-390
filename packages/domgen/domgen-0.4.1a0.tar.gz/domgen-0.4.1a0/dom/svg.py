import typing

from .base_classes import Container, Element
from .media import SVG, ScalableVectorGraphic
from .metadata import Style
from .scripts import Script
from .semantics import A, Anchor


def snake_to_camel(name: str) -> str:
    """Convert the snake_case `name` into camelCase."""
    parts = name.split("_")
    return parts[0] + "".join(map(str.title, parts[1:]))


def normalise_camelcase_attributes(
    attributes: typing.Dict[str, typing.Any], *names: str
):
    """Update `attributes` in-place such that any keys in `names` are replaced
    with their camelCase equivalents.

    For example, `attribute_name` -> `attributeName`
    """
    for name in names:
        value = attributes.pop(name, None)
        if value is not None:
            attributes[snake_to_camel(name)] = value


SVG_CAMELCASE_ATTRIBUTES = [
    "attribute_name",
    "attribute_type",
    "auto_reverse",
    "base_frequency",
    "base_profile",
    "calc_mode",
    "clip_path_units",
    "content_script_type",
    "content_style_type",
    "diffuse_constant",
    "edge_mode",
    "filter_res",
    "filter_units",
    "gradient_transform",
    "gradient_units",
    "kernel_matrix",
    "kernel_unit_length",
    "key_points",
    "key_splines",
    "key_times",
    "length_adjust",
    "limiting_cone_angle",
    "marker_height",
    "marker_units",
    "marker_width",
    "mask_content_units",
    "mask_units",
    "num_octaves",
    "path_length",
    "pattern_content_units",
    "pattern_transform",
    "pattern_units",
    "points_at_x",
    "points_at_y",
    "points_at_z",
    "preserve_alpha",
    "preserve_aspect_ratio",
    "primitive_units",
    "ref_x",
    "ref_y",
    "repeat_count",
    "repeat_dur",
    "required_extensions",
    "required_features",
    "specular_constant",
    "specular_exponent",
    "spread_method",
    "start_offset",
    "std_deviation",
    "stitch_tiles",
    "surface_scale",
    "system_language",
    "table_values",
    "target_x",
    "target_y",
    "text_length",
    "view_box",
    "view_target",
    "x_channel_selector",
    "y_channel_selector",
    "zoom_and_pan",
]


class SvgElement(Container):
    """An SVG Container element. This class exists simply to make handling SVG's
    camelCase attributes easier.
    """

    __slots__ = ()

    def __init__(self, *content: Element, **attributes: typing.Any) -> None:
        normalise_camelcase_attributes(attributes, *SVG_CAMELCASE_ATTRIBUTES)
        super().__init__(*content, **attributes)

    def serialise(self, minify: bool = True) -> str:
        if self.content:
            return Container.serialise(self, minify=minify)
        else:
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


class Animate(SvgElement):
    """The SVG `<animate>` element provides a way to animate an attribute over
    time.
    """

    __slots__ = ()
    tag = "animate"


class AnimateMotion(SvgElement):
    """The SVG `<animateMotion>` element provides a way to define how an element
    moves along a motion path.
    """

    __slots__ = ()
    tag = "animateMotion"


class AnimateTransform(SvgElement):
    """The `animateTransform` element animates a transformation attribute on its
    target element, thereby allowing animations to control translation, scaling,
    rotation, and/or skewing.
    """

    __slots__ = ()
    tag = "animateTransform"


class Circle(SvgElement):
    """The `<circle>` SVG element is an SVG basic shape, used to draw circles
    based on a centre point and a radius.
    """

    __slots__ = ()
    tag = "circle"


class ClippingPath(SvgElement):
    """The `<clipPath>` SVG element defines a clipping path, to be used by the
    `clip-path` (`clip_path`) property.

    A clipping path restricts the region to which paint can be applied.
    Conceptually, parts of the drawing that lie outside of the region bounded by
    the clipping path are not drawn.
    """

    __slots__ = ()
    tag = "clipPath"


ClipPath = ClippingPath


class Cursor(SvgElement):
    """The `<cursor>` SVG element is used to define a platform-independent
    custom cursor. A recommended approach for defining a platform-independent
    custom cursor is to create a PNG image and define a `cursor` element that
    references the PNG image and identifies the exact position within the image
    which is the pointer position (i.e., the hot spot).

    The PNG format is recommended because it supports the ability to define a
    transparency mask via an alpha channel. If a different image format is used,
    this format should support the definition of a transparency mask (two
    options: provide an explicit alpha channel or use a particular pixel colour
    to indicate transparency). If the transparency mask can be determined, the
    mask defines the shape of the cursor; otherwise, the cursor is an opaque
    rectangle. Typically, the other pixel information (e.g., the R, G, and B
    channels) defines colours for those parts of the cursor which are not masked
    out. Note that cursors usually contain at least two colours so that the
    cursor can be visible over most backgrounds.
    """

    __slots__ = ()
    tag = "cursor"


class Definitions(SvgElement):
    """The `<defs>` element is used to store graphical objects that will be used
    at a later time. Objects created inside a `<defs>` element are not rendered
    directly. To display them you have to reference them (with a `<use>` element
    for example).

    Graphical objects can be referenced from anywhere, however, defining these
    objects inside of a `<defs>` element promotes understandability of the SVG
    content and is beneficial to the overall accessibility of the document.
    """

    __slots__ = ()
    tag = "defs"


Defs = Definitions


class Description(SvgElement):
    """The `<desc>` element provides an accessible, long-text description of any
    SVG container element or graphics element.

    Text in a `<desc>` element is not rendered as part of the graphic. If the
    element can be described by visible text, it is possible to reference that
    text with the `aria-describedby` (`aria_describedby`) attribute. If
    `aria-describedby` is used, it will take precedence over `<desc>`.

    The hidden text of a `<desc>` element can also be concatenated with the
    visible text of other elements using multiple IDs in an `aria-describedby`
    value. In that case, the `<desc>` element must provide an ID for reference.
    """

    __slots__ = ()
    tag = "desc"


Desc = Description


class Ellipse(SvgElement):
    """The `<ellipse>` element is an SVG basic shape, used to create ellipses
    based on a centre coordinate, and both their x and y radius.
    """

    __slots__ = ()
    tag = "ellipse"


class FilterEffectBlend(SvgElement):
    """The `<feBlend>` SVG filter primitive composes two objects together ruled
    by a certain blending mode. This is similar to what is known from image
    editing software when blending two layers. The mode is defined by the
    `mode` attribute.
    """

    __slots__ = ()
    tag = "feBlend"


FEBlend = FilterEffectBlend


class FilterEffectColourMatrix(SvgElement):
    """The `<feColorMatrix>` SVG filter element changes colours based on a
    transformation matrix. Every pixel's colour value `[R,G,B,A]` is matrix
    multiplied by a 5 by 5 colour matrix to create new colour `[R',G',B',A']`.

    `values` may be provided as a 2D array, which will be serialised to the
    correct format.
    """

    __slots__ = ("values",)
    tag = "feColorMatrix"
    values: typing.List[typing.List[float]] | str | None

    def __init__(self, *content: Element, **attributes: typing.Any) -> None:
        self.values = attributes.pop("values", None)
        super().__init__(*content, **attributes)

    def serialise(self, minify: bool = True) -> str:
        if self.values is not None:
            if isinstance(self.values, str):
                values = self.values
            elif minify:
                values = " ".join(" ".join(map(str, row)) for row in self.values)
            else:
                values = (
                    "\n    "
                    + "\n    ".join(" ".join(map(str, row)) for row in self.values)
                    + "\n"
                )
            self.attributes["values"] = values
        return super().serialise(minify=minify)


FilterEffectColorMatrix = FilterEffectColourMatrix
FEColourMatrix = FilterEffectColourMatrix
FEColorMatrix = FilterEffectColourMatrix


class FilterEffectComponentTransfer(SvgElement):
    """The `<feComponentTransfer>` SVG filter primitive performs
    colour-component-wise remapping of data for each pixel. It allows operations
    like brightness adjustment, contrast adjustment, colour balance, or
    thresholding.

    The calculations are performed on non-premultiplied colour values. The
    colours are modified by changing each channel (R, G, B, and A) to the result
    of what the children `<feFuncR>`, `<feFuncG>`, `<feFuncB>`, and `<feFuncA>`
    return. If more than one of the same element is provided, the last one
    specified is used, and if no element is supplied to modify one of the
    channels, the effect is the same as if an identity transformation had been
    given for that channel.
    """

    __slots__ = ()
    tag = "feComponentTransfer"


FEComponentTransfer = FilterEffectComponentTransfer


class FilterEffectComposite(SvgElement):
    """The `<feComposite>` SVG filter primitive performs the combination of two
    input images pixel-wise in image space using one of the Porter-Duff
    compositing operations: `over`, `in`, `atop`, `out`, `xor`, `lighter`, or
    `arithmetic`.
    """

    __slots__ = ()
    tag = "feComposite"


FEComposite = FilterEffectComposite


class FilterEffectConvolveMatrix(SvgElement):
    """The `<feConvolveMatrix>` SVG filter primitive applies a matrix
    convolution filter effect. A convolution combines pixels in the input image
    with neighbouring pixels to produce a resulting image. A wide variety of
    imaging operations can be achieved through convolutions, including blurring,
    edge detection, sharpening, embossing and bevelling.
    """

    __slots__ = ()
    tag = "feConvolveMatrix"


FEConvolveMatrix = FilterEffectConvolveMatrix


class FilterEffectDiffuseLighting(SvgElement):
    """The `<feDiffuseLighting>` SVG filter primitive lights an image using the
    alpha channel as a bump map. The resulting image, which is an RGBA opaque
    image, depends on the light colour, light position, and surface geometry of
    the input bump map.

    The light map produced by this filter primitive can be combined with a
    texture image using the multiply term of the `arithmetic` operator of the
    `<feComposite>` filter primitive. Multiple light sources can be simulated by
    adding several of these light maps together before applying it to the
    texture image.
    """

    __slots__ = ()
    tag = "feDiffuseLighting"


FEDiffuseLighting = FilterEffectDiffuseLighting


class FilterEffectDisplacementMap(SvgElement):
    """The `<feDisplacementMap>` SVG filter primitive uses the pixel values from
    the image from `in2` to spatially displace the image from `in`.
    """

    __slots__ = ()
    tag = "feDisplacementMap"


FEDisplacementMap = FilterEffectDisplacementMap


class FilterEffectDistantLight(SvgElement):
    """The `<feDistantLight>` filter primitive defines a distant light source
    that can be used within a lighting filter primitive: `<feDiffuseLighting>`
    or `<feSpecularLighting>`.
    """

    __slots__ = ()
    tag = "feDistantLight"


FEDistantLight = FilterEffectDistantLight


class FilterEffectDropShadow(SvgElement):
    """The `<feDropShadow>` filter primitive creates a drop shadow of the input
    image. It can only be used inside a `<filter>` element.
    """

    __slots__ = ()
    tag = "feDropShadow"


FEDropShadow = FilterEffectDropShadow


class FilterEffectFlood(SvgElement):
    """The `<feFlood>` SVG filter primitive fills the filter subregion with the
    colour and opacity defined by `flood-color` (`flood_colour` or
    `flood_color`, with `flood_colour` taking priority if both are present) and
    `flood-opacity` (`flood_opacity`).
    """

    __slots__ = ()
    tag = "feFlood"


FEFlood = FilterEffectFlood


class FilterEffectFunctionRed(SvgElement):
    """The `<feFuncR>` SVG filter primitive defines the transfer function for
    the red component of the input graphic of its parent `<feComponentTransfer>`
    element.
    """

    __slots__ = ()
    tag = "feFuncR"


FEFuncR = FilterEffectFunctionRed


class FilterEffectFunctionGreen(SvgElement):
    """The `<feFuncG>` SVG filter primitive defines the transfer function for
    the green component of the input graphic of its parent
    `<feComponentTransfer>` element.
    """

    __slots__ = ()
    tag = "feFuncG"


FEFuncG = FilterEffectFunctionGreen


class FilterEffectFunctionBlue(SvgElement):
    """The `<feFuncB>` SVG filter primitive defines the transfer function for
    the blue component of the input graphic of its parent
    `<feComponentTransfer>` element.
    """

    __slots__ = ()
    tag = "feFuncB"


FEFuncB = FilterEffectFunctionBlue


class FilterEffectFunctionAlpha(SvgElement):
    """The `<feFuncA>` SVG filter primitive defines the transfer function for
    the alpha component of the input graphic of its parent
    `<feComponentTransfer>` element.
    """

    __slots__ = ()
    tag = "feFuncA"


FEFuncA = FilterEffectFunctionAlpha


class FilterEffectGaussianBlur(SvgElement):
    """The `<feGaussianBlur>` SVG filter primitive blurs the input image by the
    amount specified in `stdDeviation` (`std_deviation`), which defines the
    bell-curve.
    """

    __slots__ = ()
    tag = "feGaussianBlur"


FEGaussianBlur = FilterEffectGaussianBlur


class FilterEffectImage(SvgElement):
    """The `<feImage>` SVG filter primitive fetches image data from an external
    source and provides the pixel data as output (meaning if the external source
    is an SVG image, it is rasterised.)
    """

    __slots__ = ()
    tag = "feImage"


FEImage = FilterEffectImage


class FilterEffectMerge(SvgElement):
    """The `<feMerge>` SVG element allows filter effects to be applied
    concurrently instead of sequentially. This is achieved by other filters
    storing their output via the `result` attribute and then accessing it in a
    `<feMergeNode>` child.
    """

    __slots__ = ()
    tag = "feMerge"


FEMerge = FilterEffectMerge


class FilterEffectMergeNode(SvgElement):
    """The `feMergeNode` takes the result of another filter to be processed by
    its parent `<feMerge>`.
    """

    __slots__ = ()
    tag = "feMergeNode"


FEMergeNode = FilterEffectMergeNode


class FilterEffectMorphology(SvgElement):
    """The `<feMorphology>` SVG filter primitive is used to erode or dilate the
    input image. Its usefulness lies especially in fattening or thinning
    effects.
    """

    __slots__ = ()
    tag = "feMorphology"


FEMorphology = FilterEffectMorphology


class FilterEffectOffset(SvgElement):
    """The `<feOffset>` SVG filter primitive allows to offset the input image.
    The input image as a whole is offset by the values specified in the `dx` and
    `dy` attributes.
    """

    __slots__ = ()
    tag = "feOffset"


FEOffset = FilterEffectOffset


class FilterEffectPointLight(SvgElement):
    """The `<fePointLight>` filter primitive defines a light source which allows
    to create a point light effect. It can be used within a lighting filter
    primitive: `<feDiffuseLighting>` or `<feSpecularLighting>`.
    """

    __slots__ = ()
    tag = "fePointLight"


FEPointLight = FilterEffectPointLight


class FilterEffectSpecularLighting(SvgElement):
    """The `<feSpecularLighting>` SVG filter primitive lights a source graphic
    using the alpha channel as a bump map. The resulting image is an RGBA image
    based on the light colour. The lighting calculation follows the standard
    specular component of the Phong lighting model. The resulting image depends
    on the light colour, light position and surface geometry of the input bump
    map. The result of the lighting calculation is added. The filter primitive
    assumes that the viewer is at infinity in the z direction.

    This filter primitive produces an image which contains the specular
    reflection part of the lighting calculation. Such a map is intended to be
    combined with a texture using the `add` term of the arithmetic
    `<feComposite>` method. Multiple light sources can be simulated by adding
    several of these light maps together before applying it to the texture
    image.
    """

    __slots__ = ()
    tag = "feSpecularLighting"


FESpecularLighting = FilterEffectSpecularLighting


class FilterEffectSpotLight(SvgElement):
    """The `<feSpotLight>` filter primitive defines a light source which allows
    to create a spotlight effect. It can be used within a lighting filter
    primitive: `<feDiffuseLighting>` or `<feSpecularLighting>`.
    """

    __slots__ = ()
    tag = "feSpotLight"


FESpotLight = FilterEffectSpotLight


class FilterEffectTile(SvgElement):
    """The `<feTile>` SVG filter primitive allows to fill a target rectangle
    with a repeated, tiled pattern of an input image. The effect is similar to
    the one of a `<pattern>`.
    """

    __slots__ = ()
    tag = "feTile"


FETile = FilterEffectTile


class FilterEffectTurbulence(SvgElement):
    """The `<feTurbulence>` SVG filter primitive creates an image using the
    Perlin turbulence function. It allows the synthesis of artificial textures
    like clouds or marble. The resulting image will fill the entire filter
    primitive subregion.
    """

    __slots__ = ()
    tag = "feTurbulence"


FETurbulence = FilterEffectTurbulence


class Filter(SvgElement):
    """The `<filter>` SVG element defines a custom filter effect by grouping
    atomic filter primitives. It is never rendered itself, but must be used by
    the `filter` attribute on SVG elements, or the `filter` CSS property for
    SVG/HTML elements.
    """

    __slots__ = ()
    tag = "filter"


class ForeignObject(SvgElement):
    """The `<foreignObject>` SVG element includes elements from a different XML
    namespace. In the context of a browser, it is most likely (X)HTML.
    """

    __slots__ = ()
    tag = "foreignObject"


class Group(SvgElement):
    """The `<g>` SVG element is a container used to group other SVG elements.

    Transformations applied to the `<g>` element are performed on its child
    elements, and its attributes are inherited by its children. It can also
    group multiple elements to be referenced later with the `<use>` element.
    """

    __slots__ = ()
    tag = "g"


G = Group


class Image(SvgElement):
    """The `<image>` SVG element includes images inside SVG documents. It can
    display raster image files or other SVG files.

    The only image formats SVG software must support are JPEG, PNG, and other
    SVG files. Animated GIF behaviour is undefined.

    SVG files displayed with `<image>` are treated as an image: external
    resources aren't loaded, `:visited` styles aren't applied, and they cannot
    be interactive. To include dynamic SVG elements, try `<use>` with an
    external URL. To include SVG files and run scripts inside them, try
    `<object>` inside of `<foreignObject>`.
    """

    __slots__ = ()
    tag = "image"


SvgImage = Image


class Line(SvgElement):
    """The `<line>` element is an SVG basic shape used to create a line
    connecting two points. `from_` and `to` may be used to specify the points as
    tuples, rather than the `x1`, `y1`, `x2`, and `y2` attributes, which will be
    overwritten should both formats be provided.
    """

    __slots__ = ()
    tag = "line"

    def __init__(self, *content: Element, **attributes: typing.Any) -> None:
        from_ = attributes.pop("from_", None)
        to = attributes.pop("to", None)
        if from_ is not None:
            attributes["x1"], attributes["y1"] = from_
        if to is not None:
            attributes["x2"], attributes["y2"] = to
        super().__init__(*content, **attributes)


class LinearGradient(SvgElement):
    """The `<linearGradient>` SVG element lets authors define linear gradients
    to apply to other SVG elements.
    """

    __slots__ = ()
    tag = "linearGradient"


class Marker(SvgElement):
    """The `<marker>` element defines a graphic used for drawing arrowheads or
    polymarkers on a given `<path`>, `<line>`, `<polyline>` or `<polygon>`
    element.

    Markers can be attached to shapes using the `marker-start` (`marker_start`),
    `marker-mid` (`marker_mid`), and `marker-end` (`marker_end`) properties.
    """

    __slots__ = ()
    tag = "marker"


class Mask(SvgElement):
    """The `<mask>` element defines an alpha mask for compositing the current
    object into the background. A mask is used/referenced using the `mask`
    property.
    """

    __slots__ = ()
    tag = "mask"


class Metadata(SvgElement):
    """The `<metadata>` SVG element adds metadata to SVG content. Metadata is
    structured information about data. The contents of `<metadata>` should be
    elements from other XML namespaces such as RDF, FOAF, etc.
    """

    __slots__ = ()
    tag = "metadata"


class MotionPath(SvgElement):
    """The `<mpath>` sub-element for the `<animateMotion>` element provides the
    ability to reference an external `<path>` element as the definition of a
    motion path.
    """

    __slots__ = ()
    tag = "mpath"


MPath = MotionPath


class Path(SvgElement):
    """The `<path>` SVG element is the generic element to define a shape. All
    the basic shapes can be created with a path element.
    """

    __slots__ = ()
    tag = "path"


class Pattern(SvgElement):
    """The `<pattern>` element defines a graphics object which can be redrawn at
    repeated x and y-coordinate intervals ("tiled") to cover an area.

    The `<pattern>` is referenced by the `fill` and/or `stroke` attributes on
    other graphics elements to fill or stroke those elements with the referenced
    pattern.
    """

    __slots__ = ()
    tag = "pattern"


class Polygon(SvgElement):
    """The `<polygon>` element defines a closed shape consisting of a set of
    connected straight line segments. The last point is connected to the first
    point.

    For open shapes see the `<polyline>` element.

    `points` may be provided as an array of tuples, which will be serialised to
    the correct format.
    """

    __slots__ = ()
    tag = "polygon"

    def __init__(self, *content: Element, **attributes: typing.Any) -> None:
        points = attributes.pop("points", None)
        if points is not None:
            if not isinstance(points, str):
                points = " ".join(" ".join(map(str, point)) for point in points)
            attributes["points"] = points
        super().__init__(*content, **attributes)


class PolyLine(SvgElement):
    """The `<polyline>` element is an SVG basic shape that creates straight
    lines connecting several points. Typically a `polyline` is used to create
    open shapes as the last point doesn't have to be connected to the first
    point. For closed shapes see the `<polygon>` element.

    `points` may be provided as an array of tuples, which will be serialised to
    the correct format.
    """

    __slots__ = ()
    tag = "polyline"

    def __init__(self, *content: Element, **attributes: typing.Any) -> None:
        points = attributes.pop("points", None)
        if points is not None:
            if not isinstance(points, str):
                points = " ".join(" ".join(map(str, point)) for point in points)
            attributes["points"] = points
        super().__init__(*content, **attributes)


class RadialGradient(SvgElement):
    """The `<radialGradient>` SVG element lets authors define radial gradients
    to fill or stroke graphical elements.
    """

    __slots__ = ()
    tag = "radialGradient"


class Rectangle(SvgElement):
    """The `<rect>` SVG element is a basic SVG shape that draws rectangles,
    defined by their position, width, and height. The rectangles may have their
    corners rounded.

    `from_` and `to` may be used to specify the points as tuples, rather than
    the `x`, `y`, `width`, and `height` attributes, which will be overwritten
    should both formats be provided.

    If `to` is used rather than `width` and `height`, both `from_` (or `x` and
    `y`) and the values of `to` must be provided as numbers rather than strings.
    """

    __slots__ = ()
    tag = "rect"

    def __init__(self, *content: Element, **attributes: typing.Any) -> None:
        from_ = attributes.pop("from_", None)
        to = attributes.pop("to", None)
        if from_ is not None:
            attributes["x"], attributes["y"] = from_
        if to is not None:
            attributes["width"] = to[0] - attributes["x"]
            attributes["height"] = to[1] - attributes["y"]
        super().__init__(*content, **attributes)


Rect = Rectangle


class Set(SvgElement):
    """The `<set>` SVG element provides a simple means of just setting the value
    of an attribute for a specified duration.

    It supports all attribute types, including those that cannot reasonably be
    interpolated, such as string and boolean values. For attributes that can
    reasonably be interpolated, `<animate>` is usually preferred.
    """

    __slots__ = ()
    tag = "set"


class Stop(SvgElement):
    """The `<stop>` SVG element defines a colour and its position to use on a
    gradient. This element is always a child of a `<linearGradient>` or
    `<radialGradient>` element.
    """

    __slots__ = ()
    tag = "stop"


class Switch(SvgElement):
    """The `<switch>` SVG element evaluates any `requiredFeatures`
    (`required_features`), `requiredExtensions` (`required_extensions`) and
    `systemLanguage` (`system_language`) attributes on its direct child elements
    in order, and then renders the first child where these attributes evaluate
    to true.

    Other direct children will be bypassed and therefore not rendered. If a
    child element is a container element, like `<g>`, then its subtree is also
    processed/rendered or bypassed/not rendered.
    """

    __slots__ = ()
    tag = "switch"


class Symbol(SvgElement):
    """The `<symbol>` element is used to define graphical template objects which
    can be instantiated by a `<use>` element.

    The use of `<symbol>` elements for graphics that are used multiple times in
    the same document adds structure and semantics. Documents that are rich in
    structure may be rendered graphically, as speech, or as Braille, and thus
    promote accessibility.
    """

    __slots__ = ()
    tag = "symbol"


class Text(SvgElement):
    """The `<text>` SVG element defines a graphics element consisting of text.
    It's possible to apply a gradient, pattern, clipping path, mask, or filter
    to `<text>`, like any other SVG graphics element.

    If text is included in SVG not inside of a `<text>` element, it is not
    rendered. This is different than being hidden by default, as setting the
    `display` property won't show the text.
    """

    __slots__ = ()
    tag = "text"


class TextPath(SvgElement):
    """To render text along the shape of a `<path>`, enclose the text in a
    `<textPath>` element that has an `href` attribute with a reference to the
    `<path>` element.
    """

    __slots__ = ()
    tag = "textPath"


class Title(SvgElement):
    """The `<title>` element provides an accessible, short-text description of
    any SVG container element or graphics element.

    Text in a `<title>` element is not rendered as part of the graphic, but
    browsers usually display it as a tooltip. If an element can be described by
    visible text, it is recommended to reference that text with an
    `aria-labelledby` (`aria_labelledby`) attribute rather than using the
    `<title>` element.

    For backwards compatibility with SVG 1.1, `<title>` elements should be the
    first child element of their parent.
    """

    __slots__ = ()
    tag = "title"


SvgTitle = Title


class TextSpan(SvgElement):
    """The SVG `<tspan>` element defines a subtext within a `<text>` element or
    another `<tspan>` element. It allows for adjustment of the style and/or
    position of that subtext as needed.
    """

    __slots__ = ()
    tag = "tspan"


TSpan = TextSpan


class Use(SvgElement):
    """The `<use>` element takes nodes from within the SVG document, and
    duplicates them somewhere else. The effect is the same as if the nodes were
    deeply cloned into a non-exposed DOM, and then pasted where the `<use>`
    element is, much like cloned template elements.
    """

    __slots__ = ()
    tag = "use"


class View(SvgElement):
    """A view is a defined way to view the image, like a zoom level or detail
    view.
    """

    __slots__ = ()
    tag = "view"
