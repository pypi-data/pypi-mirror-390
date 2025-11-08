from PIL import Image
import struct
from pathlib import Path
from io import BytesIO
from typing import Self, cast
from piket.constants import PIKMIN_OTAKARA
import logging

logger = logging.getLogger(__file__)


class TreasureSprite:
    """Treasure Sprite data class for decoding and encoding GBA sprite data

    Follow this guide for creating custom treasures:
    1. Use `treasure.export_palette("out.pal")` to get the (*.pal) file
    2. Open YY-CHR and go to "Palette" > "Open RGB Palette (*.pal)..." and select the exported palette
    3. Set "Format" to "4BPP GBA"
    6. Set "Pattern" to "32x32(B)" for the large sprite, or "FC/NES x8" for the small sprite
    7. Create your sprite and modify the palette to your liking (shared by both small and large sprites)
    8. Export palette via "Palette" > "Save RGB Palette (*.pal)..."
    9. Export sprites via "File" > "Save Bitmap..."
    10. Use `treasure.import_palette("new_palette.pal")`
    11. Use `treasure.import_small("new_16x16.bmp")`
    12. Use `treasure.import_large("new_32x32.bmp")`

    NOTE: The palette is shared between the small and large sprites.
    """

    def __init__(
        self,
        header: bytes = bytes(2),
        palette: bytes = bytes(0x20),
        sprites: bytes = bytes(0x280),
        name: bytes = bytes(0x32),
    ):
        def check_size(b: bytes, expected: int, name: str):
            if len(b) != expected:
                raise ValueError(
                    f"Invalid {name} size for PIKMINOTAKARA block: "
                    f"expected {hex(expected)}, got: {hex(len(b))}"
                )

        check_size(header, 2, "header")
        check_size(palette, 0x20, "palette")
        check_size(sprites, 0x280, "sprites")
        check_size(name, 0x32, "name")

        self.header = header
        self.palette = bytearray(palette)
        self.sprites = bytearray(sprites)
        self.name = name

    @classmethod
    def from_bytes(cls, data: bytes | bytearray) -> Self:
        """Converts the block data into a TreasureSprite class with useful methods."""
        MAGIC_SIZE = 16
        UNK_HEADER_SIZE = 2
        PALETTE = MAGIC_SIZE + UNK_HEADER_SIZE
        PALETTE_SIZE = 0x20
        SPRITE_SML = PALETTE + PALETTE_SIZE
        SPRITE_SML_SIZE = 0x80
        SPRITE_LRG = SPRITE_SML + SPRITE_SML_SIZE
        SPRITE_LRG_SIZE = 0x200
        NAME = SPRITE_LRG + SPRITE_LRG_SIZE
        NAME_SIZE = 0x32
        END = NAME + NAME_SIZE
        if len(data) < END:
            raise ValueError(
                f"Treasure sprite data block smaller than expected: "
                f"got {hex(len(data))} but expected {hex(END)}"
            )
        header = data[MAGIC_SIZE:PALETTE]
        palette = data[PALETTE:SPRITE_SML]
        sprites = data[SPRITE_SML:NAME]
        name = data[NAME:END]
        return cls(header, palette, sprites, name)

    def encode(self) -> bytes:
        """Returns the full bytes for this PIKMINOTAKRA block. Used by the Card encoder."""
        out = bytearray()
        out.extend(PIKMIN_OTAKARA)
        out.extend(self.header)
        out.extend(self.palette)
        out.extend(self.sprites)
        out.extend(self.name)

        # validate size
        if len(out) < 0x2E4:
            logger.warning(
                f"PIKMINOTAKARA size less than expected 0x2e4, got {hex(len(out))}.\n"
                f"The block will be padded to 0x2e4."
            )
            out = out.ljust(0x2E4, b"\x00")

        elif len(out) > 0x2E4:
            raise ValueError(
                f"Card treasure sprite data is too large. "
                f"Expected <= 0x2e4, got {hex(len(out))}"
            )

        return bytes(out)

    # --- palette conversion ---
    @staticmethod
    def gba_to_rgb(col16: int) -> tuple[int, int, int]:
        r = (col16 & 0x1F) << 3
        g = ((col16 >> 5) & 0x1F) << 3
        b = ((col16 >> 10) & 0x1F) << 3
        return (r, g, b)

    @staticmethod
    def rgb_to_gba(rgb: tuple[int, int, int]):
        r, g, b = rgb
        return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)

    def get_palette_as_rgb(self) -> list[tuple[int, int, int]]:
        """Gets this treasure's palette as a list of 16 RGB values like (R, G, B)."""
        return [
            self.gba_to_rgb(struct.unpack("<H", self.palette[i : i + 2])[0])
            for i in range(0, 0x20, 2)
        ]

    def set_palette_from_rgb(self, colours: list[tuple[int, int, int]]):
        """Sets this treasure's palette from a list of 16 RGB values like (R, G, B)."""
        out = bytearray()
        for rgb in colours[:16]:
            # extends with little endian unsigned short
            out += struct.pack("<H", self.rgb_to_gba(rgb))
        self.palette = bytes(out)

    # --- tile conversion ---
    @staticmethod
    def decode_4bpp_tile(tile_bytes: bytes) -> list[list[int]]:
        """Decodes a 32 byte 8x8 4BPP tile to 8x8 list."""
        tile = [[0] * 8 for _ in range(8)]

        for y in range(8):
            for x in range(4):
                byte = tile_bytes[y * 4 + x]
                # split byte into 2 pixels
                tile[y][x * 2] = byte & 0xF
                tile[y][x * 2 + 1] = byte >> 4

        return tile

    @staticmethod
    def encode_4bpp_tile(tile: list[list[int]]) -> bytes:
        """Encodes an 8x8 list into a 32 byte 4BPP tile."""
        out = bytearray()
        for y in range(8):
            for x in range(0, 8, 2):
                # pixel A in low 4 bits
                # pixel B in high 4 bits
                out.append(tile[y][x] | (tile[y][x + 1] << 4))

        return bytes(out)

    # --- sprite encoder/decode ---
    def sprite_to_image(
        self, sprite_bytes: bytes, layout: list[list[int]], tile_count: int, width: int, height: int
    ) -> Image.Image:
        """Converts the sprite binary data to an Image, using the palette data."""

        # get tiles from sprite data
        tiles = [
            self.decode_4bpp_tile(sprite_bytes[i * 32 : (i + 1) * 32]) for i in range(tile_count)
        ]

        # new image in palette-based mode
        img = Image.new("P", (width, height))

        # get palette data
        palette = self.get_palette_as_rgb()
        flattened = sum(palette, ())
        img.putpalette(flattened)

        # individually place pixels
        for ty, row in enumerate(layout):
            for tx, tile_idx in enumerate(row):
                tile = tiles[tile_idx]
                for y in range(8):
                    for x in range(8):
                        img.putpixel((tx * 8 + x, ty * 8 + y), tile[y][x])

        return img

    def image_to_sprite(self, img: Image.Image, layout: list[list[int]], tile_count: int):
        """Converts an Image into sprite binary data."""
        img = img.convert("P")
        sprite_bytes = bytearray()

        # some gba formats have different tile layouts
        # in our case, the 16x16 and 32x32 are slightly different
        for ty, row in enumerate(layout):
            for tx, _ in enumerate(row):
                # extract 8x8 tile starting at (tx * 8, ty * 8)
                tile = [
                    [cast(int, img.getpixel((tx * 8 + x, ty * 8 + y))) for x in range(8)]
                    for y in range(8)
                ]
                sprite_bytes.extend(self.encode_4bpp_tile(tile))

        # limit total sprite bytes to tile count
        return bytes(sprite_bytes[: tile_count * 32])

    # --- public methods ---
    def export_small(self, path: str | Path | None = None) -> Image.Image:
        layout = [[0, 1], [2, 3]]
        small_sprite = self.sprites[:0x80]
        img = self.sprite_to_image(small_sprite, layout, 4, 16, 16)
        if isinstance(path, str | Path):
            img.save(path)

        return img

    def export_large(self, path: str | Path | None = None) -> Image.Image:
        layout = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [8, 9, 10, 11],
            [12, 13, 14, 15],
        ]
        large_sprite = self.sprites[0x80:0x280]
        img = self.sprite_to_image(large_sprite, layout, 16, 32, 32)
        if isinstance(path, str | Path):
            img.save(path)

        return img

    def import_small(self, sprite: str | Path | BytesIO | Image.Image):
        """Encodes a 16x16 8bpp indexed Bitmap/PNG-8 file as sprite data and adds to the card.\n
        Highly recommended guide:
        1. Use `treasure.export_palette("out.pal")` to get the (*.pal) file
        2. Open YY-CHR and go to "Palette" > "Open RGB Palette (*.pal)..." and select the exported palette
        3. Set "Format" to "4BPP GBA"
        4. Set "Pattern" to "FC/NES x8" or "32x32(A)"
        5. Create your 16x16 sprite, palette can be edited but will be shared with 32x32 sprite
        8. Export palette via "Palette" > "Save RGB Palette (*.pal)..."
        9. Export sprite via "File" > "Save Bitmap..."
        10. Use `treasure.import_palette("new_pal.pal")`
        11. Use `treasure.import_small("new_16x16.bmp")`

        NOTE: The palette is shared between the small and large sprites.
        """
        layout = [[0, 1], [2, 3]]
        if isinstance(sprite, Image.Image):
            img = sprite
        else:
            img = Image.open(sprite)

        self.sprites[:0x80] = self.image_to_sprite(img, layout, 4)

    def import_large(self, sprite: str | Path | BytesIO | Image.Image):
        layout = [
            [0, 1, 2, 3],
            [4, 5, 6, 7],
            [8, 9, 10, 11],
            [12, 13, 14, 15],
        ]
        if isinstance(sprite, Image.Image):
            img = sprite
        else:
            img = Image.open(sprite)

        self.sprites[0x80:0x280] = self.image_to_sprite(img, layout, 16)

    def import_palette(self, palette: str | Path | bytes):
        """Imports 16-bit palette data from (*.pal) file."""
        if isinstance(palette, str | Path):
            p = Path(palette)
            if not p.is_file():
                raise FileNotFoundError(
                    f"Could not import palette from file that does not exist: '{palette}'."
                )
            data = p.read_bytes()

        else:
            data = palette

        if len(data) != 0x200:
            raise ValueError(
                f"Import palette requires a 16-bit colour palette (0x200 size), "
                f"got size {hex(len(data))}."
            )

        self.palette = data[:0x20]

    def export_palette(self, path: str | Path | None = None) -> bytes:
        """Exports 16-bit palette data to (*.pal) file."""
        if isinstance(path, str | Path):
            # pad to 0x200
            palette = bytearray(self.palette).ljust(0x200, b"\x00")
            Path(path).write_bytes(palette)

        return self.palette

    def get_name(self) -> str:
        """Gets the SHIFT-JIS encoded name of this treasure, stripped of null bytes."""
        return self.name.decode("shift-jis").strip("\x00")

    def set_name(self, name: str):
        """Sets the SHIFT-JIS encoded name of this treasure. Max length 48 bytes."""
        encoded = name.encode("shift-jis")
        if len(encoded) > 48:
            raise ValueError(
                f"Treasure name must <= 48 bytes (SHIFT-JIS encoded), got {len(encoded)}"
            )

        self.name = encoded.ljust(0x32, b"\x00")
