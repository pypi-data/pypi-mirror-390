from pathlib import Path

# //////////////////////////////////////////////////////////////////////////////
class Utils:
    # --------------------------------------------------------------------------
    @staticmethod
    def combinations_proper_diheds(a0, a1, a2, a3):
        combinations = [
            (a0, a1, a2, a3),
            (a3, a2, a1, a0)
        ]
        masks = [
            (True,  True,  True,  True ),
            (True,  False, False, True ),
            (False, True,  True,  False),
        ]
        for mask in masks:
            for combo in combinations:
                yield combo, mask


    # --------------------------------------------------------------------------
    @staticmethod
    def combinations_improper_diheds(a0, a1, a2, a3):
        combinations = [
            (a0, a1, a2, a3),
            (a0, a1, a3, a2),
            (a2, a1, a0, a3),
            (a3, a1, a0, a2),
            (a2, a1, a3, a0),
            (a3, a1, a2, a0),
        ]
        masks = [
            (True,  True,  True,  True ),
            (True,  False, False, True ),
            (True,  False, True, True ),
        ]
        for mask in masks:
            for combo in combinations:
                yield combo, mask


    # --------------------------------------------------------------------------
    @staticmethod
    def solve_forcefield_path(ff_name: str) -> str:
        folder_data = Path(__file__).parent.parent / "_data"
        map_name2path = {
            "amber99sb": folder_data / "amber99sb.xml",
            "rna.ol3":   folder_data / "RNA.OL3.xml",
        }
        ff_path = map_name2path.get(ff_name.lower(), Path(ff_name))
        if not ff_path.exists():
            raise FileNotFoundError(f"Force field XML file not found: {ff_path}")
        return str(ff_path)


# //////////////////////////////////////////////////////////////////////////////
