from enum import IntEnum


# fmt: off
class Piki(IntEnum):
    NONE           = 0x00
    RED_LEFT       = 0x10
    RED_DOWN       = 0x11
    RED_RIGHT      = 0x12
    RED_UP         = 0x13
    BLUE_LEFT      = 0x20
    BLUE_DOWN      = 0x21
    BLUE_RIGHT     = 0x22
    BLUE_UP        = 0x23
    YELLOW_LEFT    = 0x30
    YELLOW_DOWN    = 0x31
    YELLOW_RIGHT   = 0x32
    YELLOW_UP      = 0x33
    BULBORB_LEFT   = 0x40
    BULBORB_DOWN   = 0x41
    BULBORB_RIGHT  = 0x42
    BULBORB_UP     = 0x43
    WOLLYHOP_LEFT  = 0x50
    WOLLYHOP_DOWN  = 0x51
    WOLLYHOP_RIGHT = 0x52
    WOLLYHOP_UP    = 0x53
# fmt: on
