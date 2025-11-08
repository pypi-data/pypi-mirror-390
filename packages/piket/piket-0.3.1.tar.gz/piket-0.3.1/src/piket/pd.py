from piket import Card
from piket.treasure import Treasure
from pathlib import Path
from textwrap import dedent

_SPRITES_PATH = (Path(__file__).parent / "treasure" / "sprites").resolve()


class PrototypeDetector:
    """Helps you extract all vanilla treasure sprite data from your raw Pikmin card files."""

    def __init__(self, sprites_path: Path = _SPRITES_PATH):
        if sprites_path.is_file():
            raise Exception(f"Unexpected file at path to sprites directory: {sprites_path}")
        sprites_path.mkdir(exist_ok=True)
        self.sprites_path = sprites_path
        self._update_missing()

    def _update_missing(self):
        SPRITES = [f.name for f in self.sprites_path.glob("*.bin") if f.is_file()]
        self.missing_sprites = {
            t.name: t.value for t in list(Treasure)[:10] if f"{t.name.lower()}.bin" not in SPRITES
        }

    def get_sprites(self, path: Path | str) -> list[str]:
        """Searches all .raw card files in the path for missing vanilla treasure sprites.

        Args:
            path (Path | str): The folder to search for .raw card files.

        Returns:
            list[str]: List of names for all found treasure sprites.
        """
        self._update_missing()
        path = Path(path)
        RAWS = [f.resolve() for f in path.glob("*.raw") if f.is_file()]
        new_sprites: list[str] = []
        for raw in RAWS:
            try:
                card = Card(raw)
            except:
                print(f"Failed to open {raw.name}, continuing...")
                continue

            print(f"Opening {raw.name}...")
            if not card.treasure:
                continue

            name = card.treasure.get_name()
            key = next(
                (k for k, v in self.missing_sprites.items() if v == name and k not in new_sprites),
                None,
            )
            if not key:
                continue

            print(f"Found missing treasure sprite data for '{key}'!")
            (self.sprites_path / f"{key.lower()}.bin").write_bytes(card.treasure.encode())
            new_sprites.append(key)

        self._update_missing()
        return new_sprites


def main():
    pd = PrototypeDetector()
    if len(pd.missing_sprites) > 0:
        print(
            dedent(
                f"""
            You are currently missing the following vanilla sprites:
            {", ".join(pd.missing_sprites.keys())}

            Don't worry, though! This tool will help you get them all.

            You will need to have all the official Pikmin e-Reader cards ready in a folder.
            These look like "Pikmin Card-e+ - 12-A001 (Japan).raw".

            In total there are 72 of these cards, but if you don't have them all this script will
            still try to extract any treasure sprites it can find.

            Enter the path to a folder with all your .raw card files here:"""
            )
        )

        while True:
            input_path = input()

            path = Path(input_path).resolve()
            if not path.is_dir():
                print("\nThat path was not recognised as a folder, please try again:")

            else:
                found = pd.get_sprites(path)
                if len(found) == 0:
                    print(
                        "I couldn't find any new treasure sprites in the provided directory, "
                        "please try again:"
                    )

                else:
                    print(
                        "Good news! I found the following treasure sprites and stored them:\n"
                        f"{", ".join(found)}\n"
                    )
                    if len(pd.missing_sprites) == 0:
                        print("You should now be able to use all vanilla treasure sprites, enjoy!")
                        exit()

                    print(
                        f"The following treasure sprites are still missing:"
                        f"{", ".join(pd.missing_sprites.keys())}"
                    )
                    print("If you'd like to try a new folder, enter it here:")

    else:
        print("All treasure sprites were found, good to go! :)")


if __name__ == "__main__":
    main()
