from pathlib import Path
from .util import to_bytes, decode, decompress, encode
from .constants import *
from pathlib import Path
from . import (
    plucking_pikmin as P,
    connecting_pikmin as C,
    marching_pikmin as M,
)
from .base.level_base import LevelBase
from .treasure import Treasure, TreasureSprite
import logging

logger = logging.getLogger(__file__)


class Card:

    levels: list[LevelBase]
    treasure: TreasureSprite | None
    raw: bytes
    decoded: bytes
    leveldata: bytes
    footer: bytes
    id: str

    def __init__(self, card: bytes | bytearray | str | Path | None):
        """Creates a new Card object from .raw bytes."""
        self.levels: list[LevelBase] = []
        self.treasure: TreasureSprite | None = None
        if card is None:
            self.footer = FOOTER_NORMAL

        else:
            in_bytes = to_bytes(card)
            in_footer = in_bytes[-5:]
            # determine type of input bytes (card.raw, card_decoded.bin, card_decompressed.bin)
            if in_footer == FOOTER_NORMAL or in_footer == FOOTER_CONNECTING_X3:
                # in bytes are decompressed level data
                # unfortunately we will have to infer a level ID based on contents
                self.leveldata = in_bytes
                raise NotImplementedError(
                    "Automatic inference of ID based on level data contents alone "
                    "has not been implemented yet."
                )

            elif in_bytes[0x1A : 0x1A + 8] == b"NINTENDO":
                # in bytes are decoded card data which needs to be decompressed
                self.decoded = in_bytes
                self.leveldata = decompress(in_bytes)

            else:
                # raw card file
                self.raw = in_bytes
                self.decoded = decode(in_bytes, partial_decode=True)
                self.leveldata = decompress(self.decoded)

            if self.decoded:
                self.id = self.decoded[-16:].decode("ascii").replace("\x00", "")

            self.footer = self.leveldata[-5:]

            # check footer offset
            # only applies to any card that isn't 3x Connecting Pikmin, since
            # they skip the initial 0x100 padding
            if self.leveldata[0] == 0xC3:
                # only nintendo and God knows why the offset is +0x100
                footer_offset = int.from_bytes(self.leveldata[1:3], "little") - 0x100
                if len(self.leveldata) != footer_offset + 5:
                    raise ValueError(
                        f"Decoded+decompressed card contained a footer offset that did not match. "
                        f"Expected length {hex(footer_offset+5)}, got {hex(len(self.leveldata))}."
                    )

            if self.id == CARD_SET_A_PLUCKING or self.id == CARD_SET_D_OLIMAR:
                """
                Set-A cards and also Set-D001/Olimar. Contains:
                - 3 x Plucking
                """
                start = LEVELS_START + LEVEL_ID_LENGTH
                full_level = LEVEL_ID_LENGTH + PLUCKING_PIKMIN_LENGTH
                for i in range(3):
                    end = min(start + full_level, len(self.leveldata) - LEVEL_FOOTER_LENGTH)
                    level_data = self.leveldata[start:end]
                    level = P.Level.from_bytes(level_data)
                    self.levels.append(level)
                    start += full_level

            elif self.id == CARD_SET_B_MARCHING or self.id == CARD_SET_D_PRESIDENT:
                """
                Set-B cards and also Set-D002/President. Contains:
                - 3 x Marching
                """
                start = LEVELS_START * 2 + LEVEL_ID_LENGTH
                full_level = LEVEL_ID_LENGTH + MARCHING_PIKMIN_LENGTH
                for i in range(3):
                    end = start + full_level
                    level_data = self.leveldata[start:end]
                    level = M.Level.from_bytes(level_data)
                    self.levels.append(level)
                    start += full_level

            elif self.id == CARD_SET_C_CONNECTING or self.id == CARD_SET_D_LOUIE:
                """
                Set-C cards and also Set-D003/Louie. Contains:
                - 3 x Connecting
                """
                for i in range(3):
                    start = i * 0x100
                    end = min((i + 1) * 0x100, len(self.leveldata) - LEVEL_FOOTER_LENGTH)
                    level_data = self.leveldata[start:end]
                    level = C.Level.from_bytes(level_data)
                    self.levels.append(level)

            elif self.id == CARD_SETS_H_P_ALL:
                """
                Promotional cards [H001 -> H006] + [P001 -> P003]. Contains:
                - 1 x Plucking
                - 1 x Marching
                - 1 x Connecting
                """
                start = LEVELS_START + LEVEL_ID_LENGTH
                end = 0x200
                level_data = self.leveldata[start:end]
                level = P.Level.from_bytes(level_data)
                self.levels.append(level)
                # Marching Pikmin
                start = 0x200 + LEVEL_ID_LENGTH
                end = 0x400
                level_data = self.leveldata[start:end]
                level = M.Level.from_bytes(level_data)
                self.levels.append(level)
                # Connecting Pikmin
                start = 0x400
                end = len(self.leveldata) - LEVEL_FOOTER_LENGTH
                level_data = self.leveldata[start:end]
                level = C.Level.from_bytes(level_data)
                self.levels.append(level)

            else:
                raise ValueError(f"Card data contains an unrecognised ID: '{self.id}'.")

            # check for any treasure sprite data
            self._decode_treasures()

    def _decode_treasures(self) -> bool:
        """Decodes this card's PIKMINOTAKARA block if it contains one.

        Returns:
            bool: True if succeeds, False if there is no data to decode.
        """
        if not self.leveldata:
            raise Exception(
                "Unable to decode treasures without decoded and " "decompressed level data."
            )

        # make sure the block at least big enough to validate header
        if len(self.leveldata) > 0x790:
            data = self.leveldata[0x780:]
            # make sure the block starts with PIKMINOTAKARA header
            if self.leveldata[0x780:0x790] == PIKMIN_OTAKARA:
                self.treasure = TreasureSprite.from_bytes(data)
                return True

            # there shouldn't be any other blocks at 0x780, so raise exception for unknown block
            else:
                otakara_decoded = PIKMIN_OTAKARA.decode("ascii").replace("\x00", ".")

                # try to decode the block header if possible
                found_decoded = "Failed to decode!"
                try:
                    found_decoded = data[:16].decode("ascii")
                except:
                    pass

                raise ValueError(
                    f"Unrecognised header at Treasure Sprite Data offset:\n"
                    f"Expected 0x{PIKMIN_OTAKARA.hex()} ({otakara_decoded})\n"
                    f"Got 0x{data[:16].hex()} ({found_decoded})"
                )

        return False

    def set_treasure(self, treasure: Treasure):
        """Sets the treasure binary data automatically.
        IMPORTANT: This only works if you have already extracted your treasure sprites
        using the Prototype Detector. Run `python -m piket.pd` to confirm.
        """
        self.treasure = TreasureSprite.from_bytes(treasure.data)

    def encode(self, partial_encode: bool = False, raw_level: bool = False) -> bytes:
        new_leveldata = bytearray()
        for i, level in enumerate(self.levels):
            if i > 2:
                raise ValueError(
                    f"Cards are only designed to contain 3 levels, got {len(self.levels)}."
                )
            # first level always starts different (Connecting Pikmin goes straight to level data)
            if i == 0:
                if isinstance(level, P.Level):
                    # always 0x100 padding before first Plucking Pikmin level
                    new_leveldata.extend(self.leveldata[:0x100])

                elif isinstance(level, M.Level):
                    # always 0x200 padding before first Marching Pikmin level
                    new_leveldata.extend(self.leveldata[:0x200])

            assert isinstance(level, (P.Level, M.Level, C.Level))
            level_bytes = level.to_bytes()

            # size and padding is different for each level
            expected_size = 0
            padding = 0
            if isinstance(level, P.Level):
                expected_size = 0xC5
                # pad to 0x100 if its the first level in a non-Set-A and non-Set-D-Olimar card
                if i == 0 and self.id not in [CARD_SET_A_PLUCKING, CARD_SET_D_OLIMAR]:
                    padding = 0x100

            elif isinstance(level, M.Level):
                expected_size = 0x1B2
                # pad to 0x200 if its the second level in a non-Set-B and non-Set-D-President card
                if i == 1 and self.id not in [CARD_SET_B_MARCHING, CARD_SET_D_PRESIDENT]:
                    padding = 0x200

            else:
                expected_size = 0xA5
                # non-last Connecting Pikmin levels are always padded to 0x100
                if i < 2:
                    padding = 0x100
                # if its the last level, add no padding

            # validate level sizes
            if len(level_bytes) < expected_size:
                logger.warning(
                    f"Level '{level.__class__.__module__}' size less than expected "
                    f"{hex(expected_size)}, got {hex(len(level_bytes))}.\n"
                    f"The level will be padded to {hex(expected_size)}."
                )
                level_bytes = level_bytes.ljust(expected_size, b"\x00")

            elif len(level_bytes) > expected_size:
                raise ValueError(
                    f"Level '{level.__class__.__module__}' size larger than expected "
                    f"{hex(expected_size)}, got {hex(len(level_bytes))}"
                )

            # pad further if required
            if padding > 0:
                level_bytes = level_bytes.ljust(padding, b"\x00")

            # add level bytes
            new_leveldata.extend(level_bytes)

        # add PIKMINOTAKARA treasure data if necessary
        if self.treasure:
            # always pad to 0x780 for treasure data
            new_leveldata = new_leveldata.ljust(0x780, b"\x00")
            new_leveldata.extend(self.treasure.encode())

        # add footer
        new_leveldata.extend(self.footer)

        # return early if user wants raw level data bytes
        if raw_level:
            return bytes(new_leveldata)

        # rebuild raw from existing decoded data
        elif self.decoded:
            out = encode(new_leveldata, self.decoded, partial_encode)

        else:
            # reconstruct raw data from inferred data
            raise NotImplementedError(
                "Automatic decoded data construction from just level data is incomplete."
            )

        # only update self.raw if it was a full encode
        if not partial_encode:
            self.raw = out

        # return encoded (full or partial) bytes
        return bytes(out)
