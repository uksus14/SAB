from typing import overload
import string

english = string.ascii_lowercase
russian = "абвгдежзийклмнопрстуфхцчшщъыьэюя"
russian1 = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

@overload
def encode(inp: str, alph: str=english+"_") -> int: ...
@overload
def encode(inp: int, alph: str=english+"_") -> str: ...

def encode(inp: str|int, alph: str=english+"_") -> str|int:
    byte = len(alph)+1
    if isinstance(inp, int):
        answer = ""
        while inp:
            inp, ch = divmod(inp, byte)
            answer = alph[ch-1] + answer
    else:
        answer = 0
        for ch in inp.lower():
            answer = alph.index(ch)+1 + answer*byte
    return answer


from pathlib import Path

PORT = encode('SAB')
BASE_URL = f"http://127.0.0.1:{PORT}"
BASE_FOLDER = Path(__file__).parent