from .tile import Tile
from .piki import Piki
from piket.constants import (
    MARCHING_PIKMIN,
    MARCHING_PIKMIN_HEADER_LENGTH as HEADER_LEN,
    MARCHING_PIKMIN_LAYER_LENGTH as LAYER_LEN,
    MARCHING_WIDTH as WIDTH,
    MARCHING_HEIGHT as HEIGHT,
    MARCHING_PIKIS_LENGTH as PIKIS_LEN,
)
from piket.base.level_base import LevelBase
from typing import Self
import logging

logger = logging.getLogger(__file__)


class Level(LevelBase):
    def __init__(
        self,
        index: int,
        tiles: bytearray = bytearray(WIDTH * HEIGHT),
        pikis: list[tuple[int, int, int]] = [],
        raw: bytes | bytearray = bytearray(0),
        unk01: int = 0,
        use_custom_treasure: bool = False,
    ):
        super().__init__(index, WIDTH, HEIGHT, 1, [tiles], raw)
        self.pikis = pikis
        self.unk01 = unk01
        self.use_custom_treasure = use_custom_treasure

    @classmethod
    def from_bytes(cls, level: bytes | bytearray) -> Self:
        level = bytearray(level)
        index = level[0]
        unk01 = level[1]
        use_custom_treasure = level[2] > 0
        layers = level[HEADER_LEN:]
        tiles = layers[:LAYER_LEN]
        pikis_bytes = layers[LAYER_LEN : LAYER_LEN + PIKIS_LEN]
        pikis: list[tuple[int, int, int]] = []
        for i in range(0, 33, 3):  # 11 pikis total
            x = pikis_bytes[i]
            y = pikis_bytes[i + 1]
            # break if x,y = 0,0 (same as game)
            if x == 0 and y == 0:
                break

            piki_type = pikis_bytes[i + 2]
            # skip if outside range (causes game crash)
            if piki_type > 4:
                logger.warning(
                    f"Marching Pikmin level data contains unrecognised Piki "
                    "type '{piki_type}'. This will be skipped to avoid game crashes."
                )
                continue

            pikis.append((x, y, piki_type))

        return cls(index, tiles, pikis, level, unk01, use_custom_treasure)

    def to_bytes(self) -> bytes:
        raw = bytearray()
        raw.extend(MARCHING_PIKMIN)
        raw.append(self.index)
        raw.append(self.unk01)
        raw.append(0xFF if self.use_custom_treasure else 0)
        super()._to_bytes(raw)
        for i in range(0, 0x3F, 3):
            if len(self.pikis) > i // 3:
                piki = self.pikis[i // 3]
                raw.extend(piki)
            else:
                # note that the vanilla levels seem to have a random number of 0x00 0x00 0x0F
                # the game stops reading pikis as soon as it sees x=0 && y=0
                # so it doesn't matter, just extend with zeroes
                # this does unfortunately mean we will not get 1:1 input+output from vanilla levels
                raw.extend([0, 0, 0])
        return bytes(raw)

    def get_tile(self, x: int, y: int) -> Tile:
        """Gets the Tile at (x, y)."""
        value = super()._get_tile(x, y, 0)
        if value not in Tile._value2member_map_:
            raise ValueError(f"Unknown Tile with value {value}")
        return Tile(value)

    def set_tile(self, x: int, y: int, tile: Tile):
        """Sets the Tile at (x, y)."""
        super()._set_tile(x, y, tile.value, 0)

    def set_tiles(self, x: int, y: int, w: int, h: int, tile: Tile):
        """Sets the Tiles from (x, y) to (w, h)."""
        super()._set_tiles(x, y, w, h, tile.value, 0)

    def add_piki(self, x: int, y: int, piki: Piki):
        """Places a Piki at (x, y). Cannot be (0, 0)."""
        if x == 0 and y == 0:
            raise ValueError(f"Marching Pikmin does not support Pikmin at (0, 0).")
        if len(self.pikis) >= 20:
            raise ValueError("Marching Pikmin is limited to 20 Pikmin.")
        self.pikis.append((x, y, piki.value))

    def clear_all(self):
        """Sets all Tiles to value 0x60 and removes all Pikmin."""
        for i in range(self.layers):
            super()._set_tiles(0, 0, self.width, self.height, 0x60, i)
        self.clear_pikis()

    def clear_pikis(self):
        """Removes all Pikis currently in the level."""
        self.pikis.clear()
