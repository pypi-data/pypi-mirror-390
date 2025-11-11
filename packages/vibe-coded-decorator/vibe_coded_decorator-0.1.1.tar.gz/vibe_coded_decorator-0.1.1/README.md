# vibe-coded-decorator

A Python decorator that marks functions as "vibe-coded" by adding a notice to their docstrings. This notice will appear in automatic documentation tools like FastAPI's interactive docs.

## Installation

```bash
pip install vibe-coded-decorator
```

Or install from source:

```bash
pip install .
```

## Usage

Simply add the `@vibe_coded` decorator to any function:

```python
from vibe_coded_decorator import vibe_coded

@vibe_coded
def my_function():
    """This is my function."""
    return "Hello, world!"
```

The decorator will modify the function's docstring to include a notice at the beginning:

```python
print(my_function.__doc__)
# Output: **THIS FUNCTION HAS BEEN VIBE CODED**
#
# This is my function.
```

### With FastAPI

The decorator works seamlessly with FastAPI, and the notice will appear in the automatic API documentation:

![Screenshot](screenshot.png)


```python
from fastapi import FastAPI
from vibe_coded_decorator import vibe_coded

app = FastAPI()

@app.get("/hello")
@vibe_coded
def hello_world():
    """Returns a greeting message."""
    return {"message": "Hello, world!"}
```

When you visit the FastAPI docs at `/docs`, you'll see "**THIS FUNCTION HAS BEEN VIBE CODED**" at the top of the function's description.

### Functions Without Docstrings

The decorator also works with functions that don't have docstrings:

```python
@vibe_coded
def no_docstring():
    pass

print(no_docstring.__doc__)
# Output: **THIS FUNCTION HAS BEEN VIBE CODED**
```

## Development

To install in development mode:

```bash
pip install -e .
```

## License

MIT

