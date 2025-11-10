import typing

from .base_classes import Container, Element, Void


class Area(Void):
    """The HTML `<area>` element defines a hot-spot region on an image, and
    optionally associates it with a hypertext link. This element is used only
    within a `<map>` element.

    ```html
    <map name="infographic">
        <area shape="rect" coords="184,6,253,27"
            href="https://mozilla.org"
            target="_blank" alt="Mozilla" />
        <area shape="circle" coords="130,136,60"
            href="https://developer.mozilla.org/"
            target="_blank" alt="MDN" />
        <area shape="poly" coords="130,6,253,96,223,106,130,39"
            href="https://developer.mozilla.org/docs/Web/Guide/Graphics"
            target="_blank" alt="Graphics" />
        <area shape="poly" coords="253,96,207,241,189,217,223,103"
            href="https://developer.mozilla.org/docs/Web/HTML"
            target="_blank" alt="HTML" />
        <area shape="poly" coords="207,241,54,241,72,217,189,217"
            href="https://developer.mozilla.org/docs/Web/JavaScript"
            target="_blank" alt="JavaScript" />
        <area shape="poly" coords="54,241,6,97,36,107,72,217"
            href="https://developer.mozilla.org/docs/Web/API"
            target="_blank" alt="Web APIs" />
        <area shape="poly" coords="6,97,130,6,130,39,36,107"
            href="https://developer.mozilla.org/docs/Web/CSS"
            target="_blank" alt="CSS" />
    </map>
    <img usemap="#infographic" src="/media/examples/mdn-info.png"
        alt="MDN infographic" />
    ```
    """

    __slots__ = ()
    tag = "area"


class AudioPlayer(Container):
    """The HTML `<audio>` element is used to embed sound content in documents.
    It may contain one or more audio sources, represented using the src
    attribute or the `<source>` element: the browser will choose the most
    suitable one. It can also be the destination for streamed media, using a
    `MediaStream`.

    ```html
    <audio
        controls
        src="/media/cc0-audio/t-rex-roar.mp3">
            Your browser does not support the
            <code>audio</code> element.
    </audio>
    ```
    """

    __slots__ = ()
    tag = "audio"


Audio = AudioPlayer


class VideoPlayer(Container):
    """The HTML Video element (`<video>`) embeds a media player which supports
    video playback into the document. You can use `<video>` for audio content
    as well, but the `<audio>` element may provide a more appropriate user
    experience.
    """

    __slots__ = ()
    tag = "video"


Video = VideoPlayer


class Image(Void):
    """The HTML `<img>` element embeds an image into the document.

    This is *not* the SVG element `<image>`, and using this element inside SVG
    will therefore not work. If you're using SVG, you want `dom.svg.Image` or
    `dom.SvgImage`."""

    __slots__ = ()
    tag = "img"

    def apply_attributes(self, attributes: typing.Dict[str, typing.Any]) -> None:
        return super().apply_attributes(attributes)


Img = Image


class ImageMap(Container):
    """The HTML `<map>` element is used with `<area>` elements to define an
    image map (a clickable link area).
    """

    __slots__ = ()
    tag = "map"


Map = ImageMap


class ScalableVectorGraphic(Container):
    __slots__ = ()
    tag = "svg"

    def __init__(self, *content: Element, **attributes: typing.Any) -> None:
        attributes.setdefault("xmlns", "http://www.w3.org/2000/svg")
        view_box = attributes.pop("view_box", None)
        if isinstance(view_box, (list, tuple)):
            view_box = " ".join(str(x) for x in view_box)
        if view_box is not None:
            attributes["viewBox"] = view_box
        super().__init__(*content, **attributes)


SVG = ScalableVectorGraphic


class Track(Void):
    """The HTML `<track>` element is used as a child of the media elements,
    `<audio>` and `<video>`. It lets you specify timed text tracks (or
    time-based data), for example to automatically handle subtitles. The
    tracks are formatted in WebVTT format (.vtt files) — Web Video Text Tracks

    ```html
    <video controls
        src="/media/cc0-videos/friday.mp4">
        <track default
            kind="captions"
            srclang="en"
            src="/media/examples/friday.vtt" />
        Sorry, your browser doesn't support embedded videos.
    </video>
    ```

    ## Attributes

    - `default`
        - This attribute indicates that the track should be enabled unless the
            user's preferences indicate that another track is more
            appropriate. This may only be used on one `track` element per
            media element.
    - `kind`
        - How the text track is meant to be used. If omitted the default kind
            is `subtitles`. If the attribute contains an invalid value, it
            will use `metadata` (Versions of Chrome earlier than 52 treated an
            invalid value as `subtitles`). The following keywords are allowed:
        - `subtitles`
            - Subtitles provide translation of content that cannot be
                understood by the viewer. For example dialogue or text that
                is not English in an English language film.
            - Subtitles may contain additional content, usually extra
                background information. For example the text at the beginning
                of the Star Wars films, or the date, time, and location of a
                scene.
        - `captions`
            - Closed captions provide a transcription and possibly a
                translation of audio.
            - It may include important non-verbal information such as music
                cues or sound effects. It may indicate the cue's source (e.g.
                music, text, character).
            - Suitable for users who are deaf or when the sound is muted.
        - `descriptions`
            - Textual description of the video content.
            - Suitable for users who are blind or where the video cannot be
                seen.
        - `chapters`
            - Chapter titles are intended to be used when the user is
                navigating the media resource.
        - `metadata`
            - Tracks used by scripts. Not visible to the user.
    - `label`
        - A user-readable title of the text track which is used by the browser
            when listing available text tracks.
    - `src`
        - Address of the track (`.vtt` file). Must be a valid URL. This
            attribute must be specified and its URL value must have the same
            origin as the document — unless the `<audio>` or `<video>` parent
            element of the `track` element has a `crossorigin` attribute.
    - `srclang`
        - Language of the track text data. It must be a valid BCP 47 language
            tag. If the `kind` attribute is set to `subtitles`, then `srclang`
            must be defined.
    """

    __slots__ = ()
    tag = "track"
