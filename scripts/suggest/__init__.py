from scripts.suggestion import Suggest
from pathlib import Path
import importlib
for path in Path(__file__).parent.glob("*.py"):
    if path.name == "__init__.py": continue
    importlib.import_module(f"{__name__}.{path.stem}")
def clear(call: str): return []
def sab(call: str): return ["The key to strategy is not to choose a path to victory", "But to choose so that all paths lead to victory"]
clear = Suggest(r".+\.", clear)
sab = Suggest(r"sab", sab)