from .tile import Tile
from .piki import Piki
from .player import Player
from piket.constants import (
    PLUCKING_PIKMIN,
    PLUCKING_PIKMIN_HEADER_LENGTH as HEADER_LEN,
    PLUCKING_PIKMIN_LAYER_LENGTH as LAYER_LEN,
    PLUCKING_WIDTH as WIDTH,
    PLUCKING_HEIGHT as HEIGHT,
    PLUCKING_LAYERS as LAYERS,
)
from piket.base.level_base import LevelBase
from typing import Self


class Level(LevelBase):
    def __init__(
        self,
        index: int,
        tiles: bytearray = bytearray(WIDTH * HEIGHT),
        pikis: bytearray = bytearray(WIDTH * HEIGHT),
        raw: bytes | bytearray = bytearray(0),
        grid: tuple[int, int] = (0, 0),
        start: tuple[int, int] = (0, 0),
        player: Player = Player.OLIMAR,
    ):
        super().__init__(index, WIDTH, HEIGHT, LAYERS, [tiles, pikis], raw)
        self.grid = grid
        self.start = start
        self.player = player

    @classmethod
    def from_bytes(cls, level: bytes | bytearray) -> Self:
        level = bytearray(level)
        index = level[0]
        grid = level[1], level[2]
        start = level[3] % WIDTH, level[4] % HEIGHT
        player = Player.OLIMAR if level[3] < WIDTH else Player.LOUIE
        layers = level[HEADER_LEN:]
        tiles = layers[:LAYER_LEN]
        pikis = layers[LAYER_LEN : LAYER_LEN * 2]
        return cls(index, tiles, pikis, level, grid, start, player)

    def to_bytes(self) -> bytes:
        raw = bytearray()
        raw.extend(PLUCKING_PIKMIN)
        raw.append(self.index)
        raw.extend(self.grid)
        raw.append(self.start[0] + (self.width if self.player == Player.LOUIE else 0))
        raw.append(self.start[1] + (self.height if self.player == Player.LOUIE else 0))
        return super()._to_bytes(raw)

    def get_tile(self, x: int, y: int) -> Tile:
        """Gets the Tile at (x, y, layer 0)."""
        value = super()._get_tile(x, y, 0)
        if value not in Tile._value2member_map_:
            raise ValueError(f"Unknown Tile with value {value}")
        return Tile(value)

    def get_piki(self, x: int, y: int) -> Piki:
        """Gets the Piki at (x, y, layer 1)."""
        value = super()._get_tile(x, y, 2)
        if value not in Piki._value2member_map_:
            raise ValueError(f"Unknown Piki with value {value}")
        return Piki(value)

    def set_tile(self, x: int, y: int, tile: Tile | Piki):
        """Sets the (Tile | Piki) at (x, y) on the correct layer."""
        value = tile.value
        layer = self._enum_to_layer(tile)
        super()._set_tile(x, y, value, layer)

    def set_tiles(self, x: int, y: int, w: int, h: int, tile: Tile | Piki):
        """Sets the (Tiles | Pikis) from (x, y) to (w, h) on the correct layer."""
        value = tile.value
        layer = self._enum_to_layer(tile)
        super()._set_tiles(x, y, w, h, value, layer)

    def set_grid(self, tile: Tile | Piki):
        """Sets the (Tiles | Pikis) from (0, 0) to (grid_w, grid_h) on the correct layer."""
        value = tile.value
        layer = self._enum_to_layer(tile)
        super()._set_tiles(0, 0, self.grid[0], self.grid[1], value, layer)

    def clear_all(self):
        """Sets all Tiles and Pikis to value 0."""
        for i in range(self.layers):
            super()._set_tiles(0, 0, self.width, self.height, 0, i)

    def _enum_to_layer(self, tile: Tile | Piki) -> int:
        if isinstance(tile, Tile):
            return 0
        else:
            return 1
