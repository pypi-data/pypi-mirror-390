# html-compose

A library for natural HTML composition directly in Python.

Focused on fast, flexible, extensible document generation,
its goal is to make the web platform fun to work with while using
modern browser technologies.

## Quick Start

All HTML elements from the [living spec](https://html.spec.whatwg.org/multipage/)
are available to use with full type hinting:

```python
from html_compose import a

element = a(href="/logout")["Log out"]
print(element.render())
# <a href="/logout">Log out</a>
```

The `[]` syntax provides a natural way to define child elements, making the code 
resemble the HTML structure it represents.

Behind the scenes, this is `.base_element.BaseElement.append`, which accepts text, 
elements, lists, nested lists, and callables. It returns self for chaining.

Think of it as:
* `()` sets attributes
* `[]` adds children

Set non-constructor attributes with a dict:

```python
a({"@click": "alert(1)"}, href="#")["Click me"]
```

**Security**: The children of HTML elements are always HTML escaped, 
so XSS directly in the HTML is not possible.

JavaScript within HTML attribute values is always escaped. 
Just don't pass user input into JavaScript attributes.

Use `.unsafe_text()` when you need unescaped content.

All HTML nodes treat their children as if they contain HTML.
This means if you have a `<script>` or `<style>` element or something
else that isn't read as HTML, you may need to handle escaping yourself before
passing to `.unsafe_text()`.

### Imports

You can import elements from this module or `html_compose.elements`:

- `from html_compose import a, div, span`
- `from html_compose.elements import a, div, span`
- `import html_compose.elements as el`

### Building Documents

Use `document_generator` for complete HTML5 documents with optimized resource management:

```python
from html_compose import p
from html_compose.document import document_generator
from html_compose.resource import js_import, css_import

# Local module with cache-busting
admin_script = js_import(
    "./static/admin.js",
    name="admin",
    cache_bust=True,
    preload=True
)

# Remote library
alpine = js_import(
    'https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js',
    defer=True
)

# CSS with integrity checking and preload
bootstrap_css = css_import(
    "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css",
    preload=True,
    hash="sha384-9ndCyUaIbzAi2FUVXJi0CjmCapSmO7SnpJef0486qhLnuZ2cdeRhO02iuK6FUUVM",
    crossorigin="anonymous"
)

doc = document_generator(
    title="My App",
    css=[bootstrap_css],
    js=[admin_script, alpine],
    head_extra=[],  # anything you want to add to head
    body_content=[
        p(class_="container")["Hello, world!"]
    ]
)
```

Generates HTML with correct `<link>`, `<script>`, `importmap`, and preload tags 
in the optimal order.

For streaming responses, use `document_streamer` to send the `<head>` early.

### Basic Document API

If you prefer simpler boilerplate generation, `HTML5Document` returns a complete 
document string:

```python
from html_compose import HTML5Document, p, script, link

doc = HTML5Document(
    "Site Title",
    lang="en",
    head=[
        script(src="/public/bundle.js"),
        link(rel="stylesheet", href="/public/style.css"),
    ],
    body=[p["Hello, world!"]],
)
```

### Composing Elements

The constructor for an element defines attributes, so if it has none the call
to the constructor can be skipped like the `p` and `strong` elements below:

```python
from html_compose import div, strong, a

user = "github wanderer"
content = div(class_="profile")[
    p["Welcome, ", strong[user], "!"],
    a(href="/logout")["Log out"]
]

print(content.render())
# <div class="profile"><p>Welcome, <strong>github wanderer</strong>!</p><a href="/logout">Log out</a></div>
```

## More Features

### Custom Elements

Create custom elements with `CustomElement.create` or `create_element`:

```python
from html_compose.custom_element import CustomElement

foo = CustomElement.create("foo")
foo["Hello world"].render()  # <foo>Hello world</foo>

# Or use the shorthand
from html_compose import create_element

bar = create_element("bar")
bar()["Hello world"].render()  # <bar>Hello world</bar>
```

### Type Hints

All elements and attributes are fully type-hinted for IDE support. Your editor 
can complete element names and attributes.

### Flexible Attributes

Attributes support multiple input formats:

```python
img([img.hint.src("..."), {"@click": "..."}, onmouseleave="..."])
```

### Extensions

Custom attributes for frameworks can be packaged as reusable modules:

```python
from pretend_extensions import htmx
from html_compose import button, div

button([htmx.get('/url'), htmx.target('#result')])
# <button hx-get="/url" hx-target="#result"></button>
```

## Command-line Interface

Convert HTML to html-compose syntax—useful when starting from tutorials or templates:

```sh
html-compose convert {filename or empty for stdin}
html-compose convert --noimport el  # produces el.div() style references
```

`html-convert` provides access to this tool as shorthand.