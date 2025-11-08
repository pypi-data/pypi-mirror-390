from enum import IntEnum


# fmt: off
class Tile(IntEnum):
    GROUND          = 0x00
    FIRE            = 0x10
    WATER           = 0x11
    ELECTRICITY     = 0x12
    BULBORB         = 0x13
    POISON          = 0x14
    ROCK            = 0x20
    SOFT_ROCK_0     = 0x30 # never breaks
    SOFT_ROCK_1     = 0x31
    SOFT_ROCK_2     = 0x32
    SOFT_ROCK_3     = 0x33
    SOFT_ROCK_4     = 0x34
    SOFT_ROCK_5     = 0x35
    SOFT_ROCK_6     = 0x36
    SOFT_ROCK_7     = 0x37
    SOFT_ROCK_8     = 0x38
    SOFT_ROCK_9     = 0x39
    SOFT_ROCK_10    = 0x3A # number won't show until <= 9
    SOFT_ROCK_11    = 0x3B # number won't show until <= 9
    SOFT_ROCK_12    = 0x3C # number won't show until <= 9
    SOFT_ROCK_13    = 0x3D # number won't show until <= 9
    SOFT_ROCK_14    = 0x3E # number won't show until <= 9
    SOFT_ROCK_15    = 0x3F # number won't show until <= 9
    RED_CANDYPOP    = 0x40
    BLUE_CANDYPOP   = 0x41
    YELLOW_CANDYPOP = 0x42
    PURPLE_CANDYPOP = 0x43
    WHITE_CANDYPOP  = 0x44
    TREASURE        = 0x50
    NONE            = 0x60
# fmt: on
