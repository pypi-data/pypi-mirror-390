from abc import ABC, abstractmethod
from typing import Self


class LevelBase(ABC):
    """Abstract base class for all level types."""

    index: int
    width: int
    height: int
    layers: int
    tiles: list[bytearray]
    raw: bytes

    def __init__(
        self,
        index: int,
        width: int,
        height: int,
        layers: int = 2,
        tiles: list[bytearray] | None = None,
        raw: bytes = bytes(0),
    ):
        """Initialise a level with width, height, and layered tiles.

        Args:
            index (int): Index of this level in its game mode.
            width (int): Number of tiles horizontally.
            height (int): Number of tiles vertically.
            layers (int, optional): Number of tile layers. Defaults to 2.
            tiles (list[bytearray] | None, optional): Pre-filled tile data. Defaults to None.
            raw (bytes | None, optional): Original decoded level data. Defaults to 0.
        """
        self.index = index
        self.width = width
        self.height = height
        self.layers = layers
        self.tiles = tiles or [bytearray(width * height) * layers]
        self.raw = raw

    @classmethod
    @abstractmethod
    def from_bytes(cls, level: bytes | bytearray) -> Self:
        """Create a level from decoded level data bytes.

        Args:
            level (bytes | bytearray): Decoded level data bytes

        Returns:
            LevelBase: A new level instance.
        """
        pass

    def _to_bytes(self, raw: bytearray = bytearray()) -> bytes:
        """Extends a bytes object with this level's tile layers.

        Returns:
            bytes: Level data as bytes.
        """
        for i in range(self.layers):
            raw.extend(self.tiles[i])
        return raw

    def _get_tile(self, x: int, y: int, layer: int) -> int:
        """Gets the tile at (x, y, layer).

        Returns:
            int: The exact tile value from bytes.
        """
        if not (0 <= layer < len(self.tiles)):
            raise IndexError(f"Invalid layer {layer}")
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise IndexError(f"Invalid position ({x}, {y})")
        return self.tiles[layer][y * self.width + x]

    def _set_tile(self, x: int, y: int, tile: int, layer: int):
        """Sets the tile at (x, y, layer) to an int value."""
        self.tiles[layer][y * self.width + x] = tile

    def _set_tiles(self, x: int, y: int, w: int, h: int, tile: int, layer: int):
        """Sets the tiles at (x, y, w, h, layer) to an int value."""
        for ix in range(x, x + w):
            for iy in range(y, y + h):
                # * must use LevelBase._set_tile() because self may not be a LevelBase
                LevelBase._set_tile(self, ix, iy, tile, layer)
