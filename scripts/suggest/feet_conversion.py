def feet_to_cm(call: str, feet: int=0, inches: int=0):
    return f"= {30.48*(feet + inches/12)} cm"

from scripts.suggestion import Suggest
from datetime import timedelta
feet_to_cm = Suggest(r"(?P<feet>\d+)?'((?P<inches>\d+)('')?)?", feet_to_cm, cache=timedelta(days=30))