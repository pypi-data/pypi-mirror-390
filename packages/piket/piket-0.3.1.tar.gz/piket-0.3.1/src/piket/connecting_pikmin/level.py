from .tile import Tile
from .object import Object
from .piki import Piki
from piket.constants import (
    CONNECTING_PIKMIN_HEADER_LENGTH as HEADER_LEN,
    CONNECTING_PIKMIN_LAYER_LENGTH as LAYER_LEN,
    CONNECTING_WIDTH as WIDTH,
    CONNECTING_HEIGHT as HEIGHT,
    CONNECTING_LAYERS as LAYERS,
)
from piket.base.level_base import LevelBase
from typing import Self


class Level(LevelBase):
    def __init__(
        self,
        index: int,
        tiles: bytearray = bytearray(WIDTH * HEIGHT),
        objects: bytearray = bytearray(WIDTH * HEIGHT),
        pikis: bytearray = bytearray(WIDTH * HEIGHT),
        raw: bytes | bytearray = bytearray(0),
        grid: tuple[int, int] = (0, 0),
    ):
        super().__init__(index, WIDTH, HEIGHT, LAYERS, [tiles, objects, pikis], raw)
        self.grid = grid

    @classmethod
    def from_bytes(cls, level: bytes | bytearray) -> Self:
        level = bytearray(level)
        index = level[0]
        grid = level[1], level[2]
        layers = level[HEADER_LEN:]
        tiles = layers[:LAYER_LEN]
        objects = layers[LAYER_LEN : LAYER_LEN * 2]
        pikis = layers[LAYER_LEN * 2 : LAYER_LEN * 3]
        return cls(index, tiles, objects, pikis, level, grid)

    def to_bytes(self) -> bytes:
        raw = bytearray()
        # the 12-C0XX levels do not have any main leveltype header like PIKMINPUZZLE01/02
        # though, in other cards, it is sometimes prefaced with PIKMINOTAKARA
        # TODO: figure that out
        raw.append(self.index)
        raw.extend(self.grid)
        return super()._to_bytes(raw)

    def get_tile(self, x: int, y: int) -> Tile:
        """Gets the Tile at (x, y, layer 0)."""
        value = super()._get_tile(x, y, 0)
        if value not in Tile._value2member_map_:
            raise ValueError(f"Unknown Tile with value {value}")
        return Tile(value)

    def get_object(self, x: int, y: int) -> Object:
        """Gets the Object at (x, y, layer 1)."""
        value = super()._get_tile(x, y, 1)
        if value not in Object._value2member_map_:
            raise ValueError(f"Unknown Object with value {value}")
        return Object(value)

    def get_piki(self, x: int, y: int) -> Piki:
        """Gets the Piki at (x, y, layer 2)."""
        value = super()._get_tile(x, y, 2)
        if value not in Piki._value2member_map_:
            raise ValueError(f"Unknown Piki with value {value}")
        return Piki(value)

    def set_tile(self, x: int, y: int, tile: Tile | Object | Piki):
        """Sets the (Tile | Piki | Object) at (x, y) on the correct layer."""
        value = tile.value
        layer = self._enum_to_layer(tile)
        super()._set_tile(x, y, value, layer)

    def set_tiles(self, x: int, y: int, w: int, h: int, tile: Tile | Object | Piki):
        """Sets the (Tiles | Objects | Pikis) from (x, y) to (w, h) on the correct layer."""
        value = tile.value
        layer = self._enum_to_layer(tile)
        super()._set_tiles(x, y, w, h, value, layer)

    def set_grid(self, tile: Tile | Object | Piki):
        """Sets the (Tiles | Objects | Pikis) from (0, 0) to (grid_w, grid_h) on the correct layer."""
        value = tile.value
        layer = self._enum_to_layer(tile)
        super()._set_tiles(0, 0, self.grid[0], self.grid[1], value, layer)

    def clear_all(self):
        """Sets all Tiles, Objects and Pikis to value 0."""
        for i in range(self.layers):
            super()._set_tiles(0, 0, self.width, self.height, 0, i)

    def _enum_to_layer(self, tile: Tile | Object | Piki) -> int:
        if isinstance(tile, Tile):
            return 0
        elif isinstance(tile, Object):
            return 1
        else:
            return 2
