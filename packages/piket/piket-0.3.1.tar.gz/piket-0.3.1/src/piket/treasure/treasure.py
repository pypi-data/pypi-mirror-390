from enum import Enum
from pathlib import Path


class Treasure(Enum):
    # fmt: off
    TEAR_STONE            = "ティア・ストーン"
    PINK_MENACE           = "オーバーキル・レッド"
    SCIENCE_PROJECT       = "ラブリー押し葉"
    AQUATIC_MINE          = "アクアティックマイン"
    CHOCOLATE_CUSHION     = "チョコベッド"
    SUNSEED_BERRY         = "バクレツイチゴ"
    COLOSSAL_FOSSIL       = "古代生物の化石"
    HEAVY_DUTY_MAGNETIZER = "超磁性体マグナイザー"
    DANGER_CHIME          = "ミスティックドーム"
    THE_KEY               = "あのカギ"

    # custom treasures: feel free to make a PR with your own creations
    FUEL_RESERVOIR        = "Fuel Reservoir"
    # fmt: on

    @property
    def data(self) -> bytes:
        path = Path(__file__).parent / "sprites" / (self.name.lower() + ".bin")
        if not path.is_file():
            raise FileNotFoundError(
                f"Treasure sprite data for '{self.name}' was not found.\n\n"
                "If this is a vanilla treasure, then that likely means\nyou neeed to run: "
                "`python -m piket.pd` and follow the prompts to extract the sprites."
            )

        return path.read_bytes()
