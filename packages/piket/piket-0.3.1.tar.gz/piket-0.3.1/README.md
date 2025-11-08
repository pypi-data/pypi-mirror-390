# Piket: Pikmin e+ Card Tools
All-in-one package for converting and managing Pikmin e+ Cards, pronounced "picket".

Now with support for Windows, macOS (Apple Silicon), and Linux!

## Current Capabilities
- Decode `.raw` to editable level data
- Encode editable level data to `.raw`
- Built-in support for manipulating Plucking Pikmin, Connecting Pikmin, and Marching Pikmin levels, such as:
  - `set_tile` easily set a tile at (x, y), or `set_tiles` for (x, y, w, h) placement
  - `encode` to quickly and easily get your modified Card into raw format
- Export and Import custom treasure sprites (both 16x16 and 32x32) for cards with Marching Pikmin levels

## Installation
Easily include Piket in your projects with `pip`:
```
pip install piket
```

## Quick Start Guide
Use Piket as a Level Editor:
```py
# for Plucking Pikmin
from piket import Card, PluckingPikmin as P
from pathlib import Path

card = Card("12-A001.raw") # decode the card

if isinstance(card.levels[0], P.Level):
    lvl: P.Level = card.levels[0]
    lvl.clear_all() # sets all tiles and pikis to 0x0
    lvl.grid = (3, 3) # sets the level to a 3x3 grid, maximum 11x8
    lvl.start = (1, 1) # sets the starting position
    lvl.player = P.Player.LOUIE # sets the player character

    lvl.set_grid(P.Tile.GRASS) # sets all tiles in the grid (3x3) to grass
    lvl.set_tile(0, 0, P.Piki.RED) # places a red Pikmin at (0, 0)
    lvl.set_tile(2, 2, P.Tile.FIRE) # places a fire geyser at (2, 2)

Path("12-A001-New.raw").write_bytes(card.encode()) # encode the card and write
```
For more detailed usage, check the dedicated [Usage Guide](https://github.com/plxl/piket/blob/main/docs/usage_guide.md).

## Demo
Try Piket now with the **Drag-and-Drop Converter**! This demo allows you to easily drag-and-drop `.raw` files and get decoded `.bin` files -- and then vice versa! This requires `tkinterdnd2` which may not work on all platforms.
```
pip install "piket[demo]"
python -m piket.converter
```

## Acknowledgements
- [Caitsith2](https://caitsith2.com/ereader/devtools.htm): Original e-Reader Tools (nedclib)
- [Lymia](https://github.com/Lymia/nedclib): Cross-platform, open source version of Caitsith2's nedclib
- [breadbored](https://github.com/breadbored/nedclib): Maintainer of Lymia's now-archived nedclib
- [BlackShark](https://github.com/Bl4ckSh4rk): headerfix.c source code

Nintendo is the copyright and trademark holder for Pikmin, its designs and its characters. This project is free, and for educational purposes only.
