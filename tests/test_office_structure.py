import unittest
from pathlib import Path


HTML = Path(__file__).parents[1].joinpath("public", "index.html").read_text()


class OfficeStructureTest(unittest.TestCase):
    def test_maura_office_is_single_floor_and_open_roof(self):
        required = [
            "function buildOfficeArchitecture()",
            'floor1.name = "FLOOR 1"',
            'textLabel("MAURA TRANS"',
            'textLabel("MAURA PRINTING"',
            'textLabel("LOUNGE"',
            'textLabel("GAME ROOM"',
            'textLabel("PANTRY"',
        ]
        missing = [marker for marker in required if marker not in HTML]
        self.assertFalse(missing, f"missing ground-floor markers: {missing}")
        forbidden = [
            'floor2.name = "FLOOR 2"',
            "UPPER FLOOR SLAB",
            'textLabel("FLOOR 2"',
            'textLabel("BEDROOM · 4 BEDS"',
            'textLabel("LESEHAN"',
            'textLabel("BATHROOM"',
            'textLabel("BALCONY"',
            'textLabel("STAIRS"',
            'data-room="floor2"',
            'data-room="lesehan"',
            'data-room="bathroom"',
            'data-room="balcony"',
        ]
        present = [marker for marker in forbidden if marker in HTML]
        self.assertFalse(present, f"second-floor/roof markers still present: {present}")

    def test_structural_plan_uses_existing_primitive_helpers(self):
        start = HTML.index("function buildOfficeArchitecture()")
        end = HTML.index("\n}\nconst officeArchitecture", start) + 2
        architecture = HTML[start:end]
        self.assertGreaterEqual(architecture.count("box("), 12)
        self.assertNotIn("new THREE.BoxGeometry", architecture)
        self.assertNotIn("new THREE.MeshStandardMaterial", architecture)


if __name__ == "__main__":
    unittest.main()
