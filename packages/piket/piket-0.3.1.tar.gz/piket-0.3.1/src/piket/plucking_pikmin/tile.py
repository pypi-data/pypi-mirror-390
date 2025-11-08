from enum import IntEnum


# fmt: off
class Tile(IntEnum):
    NONE                = 0x00
    GRASS               = 0x01
    ROCK                = 0x02
    FIRE                = 0x03
    WATER               = 0x04
    ELECTRICITY_NODE    = 0x05
    ELECTRICTY          = 0x06
    SLIME_GRASS         = 0x9B # likely a sprite glitch
# fmt: on
