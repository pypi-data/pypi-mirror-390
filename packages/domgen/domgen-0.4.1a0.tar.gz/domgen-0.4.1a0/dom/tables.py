import typing

from .base_classes import Container, Void


class TableCaption(Container):
    """The HTML `<caption>` element specifies the caption (or title) of a
    table.
    """

    __slots__ = ()
    tag = "caption"


Caption = TableCaption


class ColumnDeclaration(Void):
    """The HTML `<col>` element defines a column within a table and is used
    for defining common semantics on all common cells. It is generally found
    within a `<colgroup>` element.

    ```html
    <table>
        <caption>Superheros and sidekicks</caption>
        <colgroup>
            <col>
            <col span="2" class="batman">
            <col span="2" class="flash">
        </colgroup>
        <tr>
            <td> </td>
            <th scope="col">Batman</th>
            <th scope="col">Robin</th>
            <th scope="col">The Flash</th>
            <th scope="col">Kid Flash</th>
        </tr>
        <tr>
            <th scope="row">Skill</th>
            <td>Smarts</td>
            <td>Dex, acrobat</td>
            <td>Super speed</td>
            <td>Super speed</td>
        </tr>
    </table>
    ```
    """

    __slots__ = ()
    tag = "col"


Col = ColumnDeclaration


class ColumnGroup(Container):
    """The HTML `<colgroup>` element defines a group of columns within a
    table.

    ```html
    <table>
        <caption>Superheros and sidekicks</caption>
        <colgroup>
            <col>
            <col span="2" class="batman">
            <col span="2" class="flash">
        </colgroup>
        <tr>
            <td> </td>
            <th scope="col">Batman</th>
            <th scope="col">Robin</th>
            <th scope="col">The Flash</th>
            <th scope="col">Kid Flash</th>
        </tr>
        <tr>
            <th scope="row">Skill</th>
            <td>Smarts</td>
            <td>Dex, acrobat</td>
            <td>Super speed</td>
            <td>Super speed</td>
        </tr>
    </table>
    ```
    """

    __slots__ = ()
    tag = "colgroup"


ColGroup = ColumnGroup


class TableDataCell(Container):
    """The HTML `<td>` element defines a cell of a table that contains data.
    It participates in the table model.
    """

    __slots__ = ()
    tag = "td"


TD = TableDataCell


class TableHeaderCell(Container):
    """The HTML `<th>` element defines a cell as header of a group of table
    cells. The exact nature of this group is defined by the scope and headers
    attributes.
    """

    __slots__ = ()
    tag = "th"


TH = TableHeaderCell


class TableRow(Container):
    """The HTML `<tr>` element defines a row of cells in a table. The row's
    cells can then be established using a mix of `<td>` (data cell) and `<th>`
    (header cell) elements.
    """

    __slots__ = ()
    tag = "tr"


TR = TableRow


class TableHead(Container):
    """The HTML `<thead>` element defines a set of rows defining the head of
    the columns of the table.
    """

    __slots__ = ()
    tag = "thead"


THead = TableHead


class TableBody(Container):
    """The HTML Table Body element (`<tbody>`) encapsulates a set of table
    rows (`<tr>` elements), indicating that they comprise the body of the
    table (`<table>`).
    """

    tag = "tbody"


TBody = TableBody


class TableFoot(Container):
    """The HTML `<tfoot>` element defines a set of rows summarising the
    columns of the table.
    """

    __slots__ = ()
    tag = "tfoot"


TFoot = TableFoot


class Table(Container):
    """The HTML `<table>` element represents tabular data — that is,
    information presented in a two-dimensional table comprised of rows and
    columns of cells containing data.
    """

    __slots__ = ()
    tag = "table"
