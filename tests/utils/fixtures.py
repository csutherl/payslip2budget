import json
from pathlib import Path

def load_json_fixture(filename: str) -> dict:
    fixture_path = Path(__file__).parent.parent / "fixtures" / filename
    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)
