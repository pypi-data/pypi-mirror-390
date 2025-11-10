# Domgen

Domgen is a library which can be used to generate minified HTML, with rich custom component support and material design components as standard.

To make a basic page's HTML code:

```py
import dom

page_model = dom.HTML(
    dom.Head(
        dom.Title("My Glorious Test Page"),
        dom.ExternalResourceLink(rel="stylesheet", href="assets/style.css")
    ),
    dom.Body(
        dom.ContentDivision(classes={"red", "centre"})(
            "My red and centred content with",
            dom.Button(onclick="alert('hello user')")(
                "a button"
            ),
            "in it",
        )
    )
)
page_code = page_model.serialise()
page_code_readable = page_model.serialise(minify=False)
```

```html
<!-- page_code -->
<!DOCTYPE html><html><head><title>My Glorious Test Page</title><link rel="stylesheet" href="assets/style.css" /></head><body><div class="red centre">My red and centred content with<button onclick="alert('hello user')">a button</button>in it</div></body></html>
<!-- page_code_readable -->
<!DOCTYPE html>
<html>
    <head>
        <title>
            My Glorious Test Page
        </title>
        <link rel="stylesheet" href="assets/style.css" />
    </head>
    <body>
        <div class="red centre">
            My red and centred content with
            <button onclick="alert('hello user')">
                a button
            </button>
            in it
        </div>
    </body>
</html>
```
