from .base_classes import Container


class Slot(Container):
    """The HTML `<slot>` element — part of the Web Components technology suite
    — is a placeholder inside a web component that you can fill with your own
    markup, which lets you create separate DOM trees and present them
    together.
    """

    __slots__ = ()
    tag = "slot"


class ContentTemplate(Container):
    """The HTML Content Template (`<template>`) element is a mechanism for
    holding HTML that is not to be rendered immediately when a page is loaded
    but may be instantiated subsequently during runtime using JavaScript.
    """

    __slots__ = ()
    tag = "template"


Template = ContentTemplate
