# insta-ui

<div align="center">

English| [简体中文](./README.zh-CN.md)

</div>

## 📖 Introduction
insta-ui is a Python-based UI library for quickly building user interfaces.

## ⚙️ Features
Three modes:

- web mode: generates a stateless web application.
- Web View mode: generates a web view application, which can be packaged as a local app (no need to start a web service).
- Zero mode: generates a pure HTML file that can run directly in a browser without installing any dependencies.

 
## 📦 Installation

Zero mode:

```
pip install instaui -U
```
```
uv add instaui
```

web mode

```
pip install instaui[web] -U
```
```
uv add instaui[web]
```

Web View mode
```
pip install instaui[webview] -U
```
```
uv add instaui[webview]
```

🖥️ Quick Start

Install the TDesign UI library:
```
uv add instaui-tdesign[web]
```

```python
# main.py
from instaui import ui
from instaui_tdesign import td

td.use(locale="en_US")

@ui.page('/')
def home():
    ui.text("Hello, world!")

ui.server(debug=True).run()
```

📚 Getting Started

Below is a simple example of summing two numbers.
The text color of the result changes dynamically based on whether the result is even or odd.

```python
from instaui import ui
from instaui_tdesign import td

td.use(locale="en_US")

@ui.page('/')
def home():
    num1 = ui.state(0)
    num2 = ui.state(0)

    # When num1 or num2 changes, result will be automatically recalculated
    @ui.computed(inputs=[num1, num2])
    def result(num1: int, num2: int):
        return num1 + num2

    # When result changes, text_color will be automatically updated
    @ui.computed(inputs=[result])
    def text_color(result: int):
        return "red" if result % 2 == 0 else "blue"

    # UI
    td.input_number(num1, theme="column")
    ui.text("+")
    td.input_number(num2, theme="column")
    ui.text("=")
    ui.text(result).style({"color": text_color})

# When deploying a web app, remove debug=True
ui.server(debug=True).run()

```


Replace ui.server().run() with ui.webview().run() to run in web view mode:

```python
...

# ui.server(debug=True).run()
ui.webview().run()

```

Methods bound with ui.computed are executed on the server side.
If you want to run calculations on the client side, use ui.js_computed.

```python
from instaui import ui
from instaui_tdesign import td

td.use(locale="en_US")

@ui.page('/')
def home():
    num1 = ui.state(0)
    num2 = ui.state(0)

    result = ui.js_computed(inputs=[num1, num2], code="(num1, num2) => num1 + num2")
    text_color = ui.js_computed(inputs=[result], code="(result) => result % 2 === 0? 'red' : 'blue'")

    # UI
    ...

...
```

In this case, all interactions are executed in the browser (client side).
With zero mode, you can generate a pure HTML file that works without installing any dependencies:

```python
from instaui import ui, zero
from instaui_tdesign import td

td.use(locale="en_US")

@ui.page('/')
def home():
    ...

zero().to_html(home, file='index.html')
```