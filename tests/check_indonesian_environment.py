#!/usr/bin/env python3
"""Structural smoke check for original Indonesian office props."""
from pathlib import Path

html = (Path(__file__).parents[1] / "public" / "index.html").read_text()
required = {
    "BENDERA MERAH PUTIH": "Indonesian flag",
    "GEROBAK BAKSO": "bakso cart",
    "KOPI KELILING": "mobile coffee cart",
    "GALON DISPENSER": "water dispenser",
    "MEJA KARAMBOL": "carrom table",
    "GORengan meeting": "meeting snacks",
    "LOUNGE SOFA TV": "lounge",
    "PANTRY": "pantry",
    "AC INDOOR": "indoor AC",
    "AC OUTDOOR": "outdoor AC",
    "SUSPENDED LED": "suspended lighting",
    "STREET LAMP": "street lighting",
}
missing = [f"{label} ({marker})" for marker, label in required.items() if marker not in html]
assert not missing, "missing environment structures: " + ", ".join(missing)
assert "function cylinder(" in html, "props must share a procedural cylinder helper"
assert "THREE.TextureLoader" not in html and ".glb" not in html and ".gltf" not in html, "props must remain procedural"
print(f"ok: {len(required)} Indonesian/environment details found; procedural-only assets")
