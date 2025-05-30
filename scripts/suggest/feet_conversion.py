def feet_to_cm(call: str, feet: str="0", inches: str=None):
    feet = float(feet)
    if inches:
        feet += float(inches)/12
    return f"= {30.48*feet} cm"

from scripts.suggest.suggestion import Suggest
from datetime import timedelta
feet_to_cm = Suggest(r"(?P<feet>\d+)?'((?P<inches>\d+)('')?)?", feet_to_cm, cache=timedelta(days=30))