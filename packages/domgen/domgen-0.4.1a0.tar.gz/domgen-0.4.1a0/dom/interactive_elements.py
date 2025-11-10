from .base_classes import Container


class DisclosureSummary(Container):
    """The HTML Disclosure Summary element (`<summary>`) element specifies a
    summary, caption, or legend for a `<details>` element's disclosure box.
    """

    __slots__ = ()
    tag = "summary"


Summary = DisclosureSummary


class Details(Container):
    """The HTML Details Element (`<details>`) creates a disclosure widget in
    which information is visible only when the widget is toggled into an
    "open" state.
    """

    __slots__ = ()
    tag = "details"


class Dialogue(Container):
    """The HTML `<dialog>` element represents a dialogue box or other
    interactive component, such as a dismissable alert, inspector, or
    subwindow.
    """

    __slots__ = ()
    tag = "dialog"


Dialog = Dialogue


class Menu(Container):
    """The HTML `<menu>` element represents a group of commands that a user
    can perform or activate. This includes both list menus, which might appear
    across the top of a screen, as well as context menus, such as those that
    might appear underneath a button after it has been clicked.

    Context menus consist of a `<menu>` element which contains `<menuitem>`
    elements for each selectable option in the menu, `<menu>` elements for
    submenus within the menu, and `<hr>` elements for separator lines to break
    up the menu's content into sections. Context menus are then attached to
    the element they're activated from using either the associated element's
    `contextmenu` attribute or, for button-activated menus attached to
    `<button>` elements, the `menu` attribute.

    Toolbar menus consist of a `<menu>` element whose content is described in
    one of two ways: either as an unordered list of items represented by
    `<li>` elements (each representing a command or option the user can
    utilise), or (if there are no `<li>` elements), flow content describing
    the available commands and options.
    """

    __slots__ = ()
    tag = "menu"
