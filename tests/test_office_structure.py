import unittest
from pathlib import Path


HTML = Path(__file__).parents[1].joinpath("public", "index.html").read_text()


class OfficeStructureTest(unittest.TestCase):
    def test_maura_office_has_two_floor_room_plan(self):
        required = [
            "function buildOfficeArchitecture()",
            'textLabel("FLOOR 1"',
            'textLabel("FLOOR 2"',
            'textLabel("MAURA TRANS"',
            'textLabel("MAURA PRINTING"',
            'textLabel("LOUNGE"',
            'textLabel("GAME ROOM"',
            'textLabel("PANTRY"',
            'textLabel("BEDROOM · 4 BEDS"',
            'textLabel("LESEHAN"',
            'textLabel("BATHROOM"',
            'textLabel("BALCONY"',
            'textLabel("STAIRS"',
        ]
        missing = [marker for marker in required if marker not in HTML]
        self.assertFalse(missing, f"missing architectural markers: {missing}")

    def test_structural_plan_uses_existing_primitive_helpers(self):
        start = HTML.index("function buildOfficeArchitecture()")
        end = HTML.index("\n}\nconst officeArchitecture", start) + 2
        architecture = HTML[start:end]
        self.assertGreaterEqual(architecture.count("box("), 20)
        self.assertNotIn("new THREE.BoxGeometry", architecture)
        self.assertNotIn("new THREE.MeshStandardMaterial", architecture)


if __name__ == "__main__":
    unittest.main()
