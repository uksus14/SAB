def feet_to_cm(call: str, feet: int=0, inches: int=0):
    return f"= {30.48*(feet + inches/12):.1f} * cm"

from scripts.suggestion import Suggest
from datetime import timedelta
feet_to_cm = Suggest(r"(?P<feet>\d+)?'((?P<inches>\d+)('')?)?", feet_to_cm, cache=timedelta(days=30))

from scripts.testing import Tester
feet_tester = Tester(feet_to_cm)
feet_tester("4'11").claim("= 149.9 * cm")