# img2hbterm

Image to Half-block ANSI art with 256-color XTerm codes.

# Installation

## As a CLI app

```
pipx install img2hbterm
```

## As a module

```
pip install img2hbterm
```

# CLI Usage

Simply convert using

```
img2hbterm image.png
```

Flags:
- `--nearest -n` uses nearest neighbor to resize the image. (useful if antialiasing makes the output look too blurry)
- `--true-color -t` uses True Color instead of XTerm 256-color. (less term support)
- `--width <int> -s <int>` set the width of the image. (default: 128)

# Module usage

```python
from img2hbterm import convert
from io import BytesIO

print( convert("path") )

# The path can be anything Pillow supports, so BytesIO works as well
print( convert(BytesIO(b"....")) )

# With all the default values included
print(
    convert(
        "path",
        nearest=False,
        true=False, # Not to be confused with the boolean True
        size=128
    )
)

# Works the same way the CLI does, I don't need to document the parameters again.
```

