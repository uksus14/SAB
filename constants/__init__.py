from pathlib import Path
import json
folder = Path(__file__).parent


with open(folder / "bangs.json", "r", encoding="utf-8") as f:
    bangs: dict[str, str] = json.load(f)
with open(folder / "freqs.json", "r", encoding="utf-8") as f:
    freqs: dict[str, int] = json.load(f)
with open(folder / "top_level_domains.txt", "r", encoding="utf-8") as f:
    top_level_domains: list[str] = f.read().split("\n")
with open(folder / "weather_codes.json", "r", encoding="utf-8") as f:
    weather_codes: dict[int, str] = {int(num): desc for num, desc in json.load(f).items()}