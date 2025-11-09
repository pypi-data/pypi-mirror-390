# img2hbirc

Image to Half-block ANSI art with IRC color codes.

# Installation

## As a CLI app

```
pipx install img2hbirc
```

## As a module

```
pip install img2hbirc
```

# CLI Usage

Simply convert using

```
img2hbirc image.png
```

Output will look weird in terminal, so you can also put it in a file

```
img2hbirc -o image.txt image.png
```

Then you can upload it so an IRC bot can output it.

Flags:
- `--nearest -n` uses nearest neighbor to resize the image. (useful if antialiasing makes the output look bad)
- `--posterize -p` uses 4-bit posterization on the image. (useful if the image has a lot of different colors)
- `--legacy-palette -l` uses the legacy 16-color mIRC color palette instead of the 84 other colors.
- `--width <int> -s <int>` set the width of the image (default: 64), a high number might cause the IRC network to truncate your message.

# Module usage

## Convert RGB color to IRC control code

```python
from img2hbirc import rgb2irc

# Regular way
print( rgb2irc(255, 0, 0) )

# mIRC palette
print( rgb2irc(255, 0, 0, legacy=True) )
```

You only get the color number as a string, so you have to embed it like

```python
f"\x03{rgb2irc(255, 0, 0)}This text is red!\x01"
```

## Convert Image

```python
from img2hbirc import convert
from io import BytesIO

print( convert("path") )

# The path can be anything Pillow supports, so BytesIO works as well
print( convert(BytesIO(b"....")) )

# With all the default values included
print(
    convert(
        "path",
        nearest=False,
        post=False,
        legacy=False,
        size=64
    )
)

# Works the same way the CLI does, I don't need to document the parameters again.
```
