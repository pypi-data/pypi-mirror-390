import typing

from .base_classes import Container, Void


class Button(Container):
    """The HTML `<button>` element represents a clickable button, used to
    submit forms or anywhere in a document for accessible, standard button
    functionality.
    """

    __slots__ = ()
    tag = "button"


class DataList(Container):
    """The HTML `<datalist>` element contains a set of `<option>` elements
    that represent the permissible or recommended options available to choose
    from within other controls.

    ```html
    <label for="ice-cream-choice">Choose a flavour:</label>
    <input list="ice-cream-flavours" id="ice-cream-choice" name="ice-cream-choice" />

    <datalist id="ice-cream-flavours">
        <option value="Chocolate">
        <option value="Coconut">
        <option value="Mint">
        <option value="Strawberry">
        <option value="Vanilla">
    </datalist>
    ```
    """

    __slots__ = ()
    tag = "datalist"


class FieldSet(Container):
    """The HTML `<fieldset>` element is used to group several controls as well
    as labels (`<label>`) within a web form.

    ```html
    <form>
        <fieldset>
            <legend>Choose your favourite monster</legend>

            <input type="radio" id="kraken" name="monster">
            <label for="kraken">Kraken</label><br/>

            <input type="radio" id="sasquatch" name="monster">
            <label for="sasquatch">Sasquatch</label><br/>

            <input type="radio" id="mothman" name="monster">
            <label for="mothman">Mothman</label>
        </fieldset>
    </form>
    ```
    """

    __slots__ = ()
    tag = "fieldset"


class Form(Container):
    """The HTML `<form>` element represents a document section containing
    interactive controls for submitting information.
    """

    __slots__ = ()
    tag = "form"


class Input(Void):
    """The HTML `<input>` element is used to create interactive controls for
    web-based forms in order to accept data from the user; a wide variety of
    types of input data and control widgets are available, depending on the
    device and user agent.

    If used directly, `type` must be provided
    """

    __slots__ = ("type",)
    tag = "input"
    type: str

    def apply_attributes(self, attributes: typing.Dict[str, typing.Any]) -> None:
        if not attributes["type"]:
            attributes["type"] = self.type
        return super().apply_attributes(attributes)


class Checkbox(Input):
    """A check box allowing single values to be selected/deselected."""

    __slots__ = ()
    type = "checkbox"


class ColourInput(Input):
    """A control for specifying a colour; opening a colour picker when active
    in supporting browsers.
    """

    __slots__ = ()
    type = "color"


ColorInput = ColourInput
Colour = ColourInput
Color = ColourInput


class DateInput(Input):
    """A control for entering a date (year, month, and day, with no time).
    Opens a date picker or numeric wheels for year, month, day when active in
    supporting browsers.
    """

    __slots__ = ()
    type = "date"


Date = DateInput


class DatetimeInput(Input):
    """A control for entering a date and time, with no time zone. Opens a date
    picker or numeric wheels for date- and time-components when active in
    supporting browsers.
    """

    __slots__ = ()
    type = "datetime-local"


DatetimeLocal = DatetimeInput


class EmailInput(Input):
    """A field for editing an email address. Looks like a text input, but has
    validation parameters and relevant keyboard in supporting browsers and
    devices with dynamic keyboards.
    """

    __slots__ = ()
    type = "email"


Email = EmailInput


class FileInput(Input):
    """A control that lets the user select a file. Use the accept attribute to
    define the types of files that the control can select.
    """

    __slots__ = ()
    type = "file"


File = FileInput


class HiddenInput(Input):
    """A control that is not displayed but whose value is submitted to the
    server. There is an example in the next column, but it's hidden!
    """

    __slots__ = ()
    type = "hidden"


Hidden = HiddenInput


class ImageButton(Input):
    """A graphical submit button. Displays an image defined by the src
    attribute. The alt attribute displays if the image src is missing.
    """

    __slots__ = ()
    type = "image"


Image = ImageButton


class MonthInput(Input):
    """A control for entering a month and year, with no time zone."""

    __slots__ = ()
    type = "month"


Month = MonthInput


class NumberInput(Input):
    """A control for entering a number. Displays a spinner and adds default
    validation when supported. Displays a numeric keypad in some devices with
    dynamic keypads.
    """

    __slots__ = ()
    type = "number"


Number = NumberInput


class PasswordInput(Input):
    """A single-line text field whose value is obscured. Will alert user if
    site is not secure.
    """

    __slots__ = ()
    type = "password"


Password = PasswordInput


class RadioButton(Input):
    """A radio button, allowing a single value to be selected out of multiple
    choices with the same name value.
    """

    __slots__ = ()
    type = "radio"


Radio = RadioButton


class RangeSlider(Input):
    """A control for entering a number whose exact value is not important.
    Displays as a range widget defaulting to the middle value. Used in
    conjunction min and max to define the range of acceptable values.
    """

    __slots__ = ()
    type = "range"


Range = RangeSlider


class ResetButton(Input):
    """A button that resets the contents of the form to default values. Not
    recommended.
    """

    __slots__ = ()
    type = "reset"


Reset = ResetButton


class SearchBox(Input):
    """A single-line text field for entering search strings. Line-breaks are
    automatically removed from the input value. May include a delete icon in
    supporting browsers that can be used to clear the field. Displays a
    search icon instead of enter key on some devices with dynamic keypads.
    """

    __slots__ = ()
    type = "search"


Search = SearchBox


class SubmitButton(Input):
    """A button that submits the form."""

    __slots__ = ()
    type = "submit"


Submit = SubmitButton


class TelephoneInput(Input):
    """A control for entering a telephone number. Displays a telephone keypad
    in some devices with dynamic keypads.
    """

    __slots__ = ()
    type = "tel"


Tel = TelephoneInput


class TextBox(Input):
    """The default value. A single-line text field. Line-breaks are
    automatically removed from the input value.
    """

    __slots__ = ()
    type = "text"


Text = TextBox


class TimeInput(Input):
    """A control for entering a time value with no time zone."""

    __slots__ = ()
    type = "time"


Time = TimeInput


class URLBox(Input):
    """A field for entering a URL. Looks like a text input, but has validation
    parameters and relevant keyboard in supporting browsers and devices with
    dynamic keyboards.
    """

    __slots__ = ()
    type = "url"


URL = URLBox


class WeekInput(Input):
    """A control for entering a date consisting of a week-year number and a
    week number with no time zone.
    """

    __slots__ = ()
    type = "week"


Week = WeekInput


class Label(Container):
    """The HTML `<label>` element represents a caption for an item in a user
    interface.

    Use `for_` for the `for` parameter (to avoid keyword conflict)
    """

    __slots__ = ()
    tag = "label"


class Legend(Container):
    """The HTML `<legend>` element represents a caption for the content of
    its parent `<fieldset>`.
    """

    __slots__ = ()
    tag = "legend"


class Meter(Container):
    """The HTML <meter> element represents either a scalar value within a
    known range or a fractional value.

    ```html
    <label for="fuel">Fuel level:</label>

    <meter id="fuel"
        min="0" max="100"
        low="33" high="66" optimum="80"
        value="50">
        at 50/100
    </meter>
    ```
    """

    __slots__ = ()
    tag = "meter"


class OptionGroup(Container):
    """The HTML `<optgroup>` element creates a grouping of options within a
    `<select>` element.

    ```html
    <label for="dino-select">Choose a dinosaur:</label>
    <select id="dino-select">
        <optgroup label="Theropods">
            <option>Tyrannosaurus</option>
            <option>Velociraptor</option>
            <option>Deinonychus</option>
        </optgroup>
        <optgroup label="Sauropods">
            <option>Diplodocus</option>
            <option>Saltasaurus</option>
            <option>Apatosaurus</option>
        </optgroup>
    </select>
    ```
    """

    __slots__ = ()
    tag = "optgroup"


OptGroup = OptionGroup


class Option(Container):
    """The HTML `<option>` element is used to define an item contained in a
    `<select>`, an `<optgroup>`, or a `<datalist>` element. As such,
    `<option>` can represent menu items in popups and other lists of items
    in an HTML document.
    """

    __slots__ = ()
    tag = "option"


class Output(Container):
    """The HTML Output element (`<output>`) is a container element into which
    a site or app can inject the results of a calculation or the outcome of a
    user action.

    ## Attributes

    - `for`
        - A space-separated list of other elements’ `id`s, indicating that
            those elements contributed input values to (or otherwise
            affected) the calculation.
    - `form`
        - The `<form>` element to associate the output with (its form owner).
            The value of this attribute must be the `id` of a `<form>` in the
            same document. (If this attribute is not set, the `<output>` is
            associated with its ancestor `<form>` element, if any.)
        - This attribute lets you associate `<output>` elements to `<form>`s
            anywhere in the document, not just inside a `<form>`. It can also
            override an ancestor `<form>` element.
    - name
        - The element's name. Used in the `form.elements` API.
        - The `<output>` value, name, and contents are NOT submitted during
            form submission.

    ```html
    <form oninput="result.value=parseInt(a.value)+parseInt(b.value)">
        <input type="range" id="b" name="b" value="50" /> +
        <input type="number" id="a" name="a" value="10" /> =
        <output name="result" for="a b">60</output>
    </form>
    ```
    """

    __slots__ = ()
    tag = "output"


class Progress(Container):
    """The HTML `<progress>` element displays an indicator showing the
    completion progress of a task, typically displayed as a progress bar.

    ```html
    <label for="file">File progress:</label>

    <progress id="file" max="100" value="70">70%</progress>
    ```
    """

    __slots__ = ()
    tag = "progress"


class Select(Container):
    """The HTML `<select>` element represents a control that provides a menu
    of options

    ```html
    <label for="pet-select">Choose a pet:</label>

    <select name="pets" id="pet-select">
        <option value="">--Please choose an option--</option>
        <option value="dog">Dog</option>
        <option value="cat">Cat</option>
        <option value="hamster">Hamster</option>
        <option value="parrot">Parrot</option>
        <option value="spider">Spider</option>
        <option value="goldfish">Goldfish</option>
    </select>
    ```
    """

    __slots__ = ()
    tag = "select"


class TextArea(Container):
    """The HTML `<textarea>` element represents a multi-line plain-text
    editing control, useful when you want to allow users to enter a sizeable
    amount of free-form text, for example a comment on a review or feedback
    form.

    ```html
    <label for="story">Tell us your story:</label>

    <textarea id="story" name="story"
        rows="5" cols="33">
    It was a dark and stormy night...
    </textarea>
    ```
    """

    __slots__ = ()
    tag = "textarea"
