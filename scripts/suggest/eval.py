from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication
from scripts.serializing import Serializers
from variables import EvalStrVar
import regex

default_eval = """#Eval variables and functions here
from math import *
from typing import Self
import hashlib
from collections import Counter
import collections
import string
from functools import reduce
from itertools import batched
import itertools
import random as rand_mod
from datetime import datetime, timedelta
from random import *
from commons import *
def choice(*choices):
    for _ in [", ", ",", " "]:
        if len(choices) != 1: break
        choices = choices[0].split(", ")
    return rand_mod.choice(choices)
def random(l=None, r=None) -> int|float:
    if l is None: return rand_mod.random()
    if r is None: return rand_mod.randint(1, l)
    return rand_mod.randint(l, r)
def simplify(top: int, bottom: int) -> tuple[int, int]:
    g = gcd(top, bottom)
    return top//g, bottom//g
def count(*args):
    ans = {}
    for arg in args:
        ans.setdefault(arg, 0)
        ans[arg] += 1
    return ans
def physics(num: float, dim: str) -> float:
    return num

#constants

meter = 1
second = 1
minute = 60*second
SEC = timedelta(seconds=1)
MIN = timedelta(minutes=1)
HOUR = timedelta(hours=1)
DAY = timedelta(days=1)
WEEK = timedelta(days=7)
MONTH = timedelta(days=30)
YEAR = timedelta(days=365)
hour = 60*minute
day = 24*hour
month = 30*day
year = 365.25*day
planck = physics(6.62607015*10**-34, 'm**2*kg*s**-1')
planck_constant = planck
speed_of_light = physics(299792458, 'm*s**-1')
lightspeed = speed_of_light
light_second = physics(second*speed_of_light, 'm')
light_minute = physics(minute*speed_of_light, 'm')
light_hour = physics(hour*speed_of_light, 'm')
light_day = physics(day*speed_of_light, 'm')
light_month = physics(month*speed_of_light, 'm')
light_year = physics(year*speed_of_light, 'm')
light_decade = physics(10*year*speed_of_light, 'm')
light_century = physics(100*year*speed_of_light, 'm')
el_H = physics(1.008, 'g*mol**-1')
el_He = physics(4.0026022, 'g*mol**-1')
el_Li = physics(6.94, 'g*mol**-1')
el_Be = physics(9.01218315, 'g*mol**-1')
el_B = physics(10.81, 'g*mol**-1')
el_C = physics(12.011, 'g*mol**-1')
el_N = physics(14.007, 'g*mol**-1')
el_O = physics(15.999, 'g*mol**-1')
el_F = physics(18.9984031636, 'g*mol**-1')
el_Ne = physics(20.17976, 'g*mol**-1')
el_Na = physics(22.989769282, 'g*mol**-1')
el_Mg = physics(24.305, 'g*mol**-1')
el_Al = physics(26.98153857, 'g*mol**-1')
el_Si = physics(28.085, 'g*mol**-1')
el_P = physics(30.9737619985, 'g*mol**-1')
el_S = physics(32.06, 'g*mol**-1')
el_Cl = physics(35.45, 'g*mol**-1')
el_Ar = physics(39.9481, 'g*mol**-1')
el_K = physics(39.09831, 'g*mol**-1')
el_Ca = physics(40.0784, 'g*mol**-1')
el_Sc = physics(44.9559085, 'g*mol**-1')
el_Ti = physics(47.8671, 'g*mol**-1')
el_V = physics(50.94151, 'g*mol**-1')
el_Cr = physics(51.99616, 'g*mol**-1')
el_Mn = physics(54.9380443, 'g*mol**-1')
el_Fe = physics(55.8452, 'g*mol**-1')
el_Co = physics(58.9331944, 'g*mol**-1')
el_Ni = physics(58.69344, 'g*mol**-1')
el_Cu = physics(63.5463, 'g*mol**-1')
el_Zn = physics(65.382, 'g*mol**-1')
el_Ga = physics(69.7231, 'g*mol**-1')
el_Ge = physics(72.6308, 'g*mol**-1')
el_As = physics(74.9215956, 'g*mol**-1')
el_Se = physics(78.9718, 'g*mol**-1')
el_Br = physics(79.904, 'g*mol**-1')
el_Kr = physics(83.7982, 'g*mol**-1')
el_Rb = physics(85.46783, 'g*mol**-1')
el_Sr = physics(87.621, 'g*mol**-1')
el_Y = physics(88.905842, 'g*mol**-1')
el_Zr = physics(91.2242, 'g*mol**-1')
el_Nb = physics(92.906372, 'g*mol**-1')
el_Mo = physics(95.951, 'g*mol**-1')
el_Tc = physics(98, 'g*mol**-1')
el_Ru = physics(101.072, 'g*mol**-1')
el_Rh = physics(102.905502, 'g*mol**-1')
el_Pd = physics(106.421, 'g*mol**-1')
el_Ag = physics(107.86822, 'g*mol**-1')
el_Cd = physics(112.4144, 'g*mol**-1')
el_In = physics(114.8181, 'g*mol**-1')
el_Sn = physics(118.7107, 'g*mol**-1')
el_Sb = physics(121.7601, 'g*mol**-1')
el_Te = physics(127.603, 'g*mol**-1')
el_I = physics(126.904473, 'g*mol**-1')
el_Xe = physics(131.2936, 'g*mol**-1')
el_Cs = physics(132.905451966, 'g*mol**-1')
el_Ba = physics(137.3277, 'g*mol**-1')
el_La = physics(138.905477, 'g*mol**-1')
el_Ce = physics(140.1161, 'g*mol**-1')
el_Pr = physics(140.907662, 'g*mol**-1')
el_Nd = physics(144.2423, 'g*mol**-1')
el_Pm = physics(145, 'g*mol**-1')
el_Sm = physics(150.362, 'g*mol**-1')
el_Eu = physics(151.9641, 'g*mol**-1')
el_Gd = physics(157.253, 'g*mol**-1')
el_Tb = physics(158.925352, 'g*mol**-1')
el_Dy = physics(162.5001, 'g*mol**-1')
el_Ho = physics(164.930332, 'g*mol**-1')
el_Er = physics(167.2593, 'g*mol**-1')
el_Tm = physics(168.934222, 'g*mol**-1')
el_Yb = physics(173.0451, 'g*mol**-1')
el_Lu = physics(174.96681, 'g*mol**-1')
el_Hf = physics(178.492, 'g*mol**-1')
el_Ta = physics(180.947882, 'g*mol**-1')
el_W = physics(183.841, 'g*mol**-1')
el_Re = physics(186.2071, 'g*mol**-1')
el_Os = physics(190.233, 'g*mol**-1')
el_Ir = physics(192.2173, 'g*mol**-1')
el_Pt = physics(195.0849, 'g*mol**-1')
el_Au = physics(196.9665695, 'g*mol**-1')
el_Hg = physics(200.5923, 'g*mol**-1')
el_Tl = physics(204.38, 'g*mol**-1')
el_Pb = physics(207.21, 'g*mol**-1')
el_Bi = physics(208.980401, 'g*mol**-1')
el_Po = physics(209, 'g*mol**-1')
el_At = physics(210, 'g*mol**-1')
el_Rn = physics(222, 'g*mol**-1')
el_Fr = physics(223, 'g*mol**-1')
el_Ra = physics(226, 'g*mol**-1')
el_Ac = physics(227, 'g*mol**-1')
el_Th = physics(232.03774, 'g*mol**-1')
el_Pa = physics(231.035882, 'g*mol**-1')
el_U = physics(238.028913, 'g*mol**-1')
el_Np = physics(237, 'g*mol**-1')
el_Pu = physics(244, 'g*mol**-1')
el_Am = physics(243, 'g*mol**-1')
el_Cm = physics(247, 'g*mol**-1')
el_Bk = physics(247, 'g*mol**-1')
el_Cf = physics(251, 'g*mol**-1')
el_Es = physics(252, 'g*mol**-1')
el_Fm = physics(257, 'g*mol**-1')
el_Md = physics(258, 'g*mol**-1')
el_No = physics(259, 'g*mol**-1')
el_Lr = physics(266, 'g*mol**-1')
el_Rf = physics(267, 'g*mol**-1')
el_Db = physics(268, 'g*mol**-1')
el_Sg = physics(269, 'g*mol**-1')
el_Bh = physics(270, 'g*mol**-1')
el_Hs = physics(269, 'g*mol**-1')
el_Mt = physics(278, 'g*mol**-1')
el_Ds = physics(281, 'g*mol**-1')
el_Rg = physics(282, 'g*mol**-1')
el_Cn = physics(285, 'g*mol**-1')
el_Nh = physics(286, 'g*mol**-1')
el_Fl = physics(289, 'g*mol**-1')
el_Mc = physics(289, 'g*mol**-1')
el_Lv = physics(293, 'g*mol**-1')
el_Ts = physics(294, 'g*mol**-1')
el_Og = physics(294, 'g*mol**-1')
el_Uue = physics(315, 'g*mol**-1')
speed_of_sound = physics(343, 'm*s**-1')
mach = speed_of_sound
earth_radius = physics(6378000, 'm')
radius_of_the_earth = earth_radius
gravitational_constant = physics(6.6743*10**-11, 'm**3*kg**-1*s**-2')
gravity = gravitational_constant
G = gravitational_constant
default_currency = 'usd'
people = 8*10**9
bang_to_check = 158
deleted = 0
astronomical_unit = physics(499*light_second, 'm')
au = astronomical_unit
parsec = physics(206265*au, 'm')
pc = parsec
Mpc = physics(1000000*pc, 'm')
picosecond = physics(10**-12, 's')
angstrom = physics(10**-10, 'm')
Avogadro = 6.022*10**23
avogadro = 6.022*10**23
R = physics(8.31446261815324, 'J*mol**-1*K**-1')
K = 273.15
cm = .01*meter
dm = .1*meter
litre = dm**3
liter = dm**3
km = 1000*meter
ln=log
mile = 1.609344*km
feet = 30.48 * cm
mph=mile/hour
kph=km/hour
digits = lambda n, base=10:[(n//(base**i))%base for i in range(int(ln(n)/ln(base))+1)]
product = lambda l: l[0]*product(l[1:]) if l else 1
kg=1
lbs=0.45359237*kg
pound=lbs
ml=liter/1000
teaspoon=4.92892159*ml
olympic_pool=2500000*liter
billion=10**9
type1paradox='logical contradiction'
type2paradox='normal impossible question'
type3paradox='counterintuitive fact'
type4paradox='math prank'
type5paradox='one guy getting very confused, writing it down, and getting it published'

#variables
"""

eval_strs = EvalStrVar.create("eval", default_eval.split("\n"), ext="py", serializer=Serializers.line_splitter())

def globs():
    import variables.eval
    return variables.eval.__dict__

def normalize_eval(query: str) -> str:
    return query.replace("^", "**").replace("->", ":")

def refresh_eval_inner(call: str) -> str:
    prev = eval_strs.data
    eval_strs.refresh()
    return "Variables refreshed!"

def search_eval_inner(call: str, query: str) -> list[str]|str:
    ans = []
    if not regex.match(r"^\/.*\/$", query): mm = lambda match: query in match
    else: mm = lambda match:regex.search(query[1:-1], match)
    for line in eval_strs.data[eval_strs.data.index("#constants"):]:
        match = regex.match(assignment_re, line, flags=regex.IGNORECASE)
        if not match: continue
        match = match.group("variable")
        if mm(match): ans.append(f"= {match}")
    return ans or "No variables found!"

def cool_eval_inner(call: str, query: str, variable: str|None=None, value: str|None=None, normalize=True) -> str:
    query = normalize_eval(query)
    if value:
        value = normalize_eval(value)
        try: return f"= {eval(value, globals=globs())}"
        except: pass
    try: return f"= {eval(query, globals=globs())}"
    except: pass
    normalized = symppy_eval_inner(call, query)
    if not normalize or normalized == "not computable": return normalized
    return f"= {eval(normalized[3:], globals=globs())}"
def symppy_eval_inner(call: str, query: str) -> str:
    query = normalize_eval(query)
    try: exp = parse_expr(query, transformations=standard_transformations + (implicit_multiplication,))
    except: return "not computable"
    return f"== {exp}"

def add_line_inner(call: str, query: str, variable: str|None=None, value: str|None=None) -> str:
    query = normalize_eval(query)
    if not cool_eval_inner(call, query).startswith("= "): return "Adding line failed!"
    def persist(line: str) -> bool:
        match = regex.match(f"^{assignment_re}$", line) or regex.match(r"^(?P<variable>\w+)[.[].+$", line)
        return match is None or match.group("variable") != variable
    if variable is None: persist = lambda l: True
    var_line = eval_strs.data.index("#variables")
    eval_strs.data = eval_strs.data[:var_line]+list(filter(persist, eval_strs.data[var_line:]))+[query]
    return "Line saved!"

assignment_re = r"(?P<variable>.*?[^!=><])=(?P<value>[^=].*)"
from scripts.suggestion import Suggest
refresh_eval = Suggest(r"==r", refresh_eval_inner)
search_eval = Suggest(r"(?P<query>.+)=\?", search_eval_inner, page=True)
cool_eval = Suggest(fr"(==? )?(?P<query>({assignment_re})|.+)=", cool_eval_inner)
symppy_eval = Suggest(r"(==? )?(?P<query>.+)==", symppy_eval_inner)
add_line = Suggest(fr"(==? )?(?P<query>({assignment_re})|.+)===", add_line_inner)

from scripts.testing import Tester
refresh_tester = Tester(refresh_eval)
refresh_tester("asdf").claim(None)
refresh_tester("==r").claim("Variables refreshed!")
def not_novarfound(ans):
    """checking if the answer is not 'No variables found!'"""
    return ans and ans != "No variables found!"
search_tester = Tester(search_eval)
search_tester("el=?").claim(not_novarfound)
search_tester("/^el.+$/=?").claim(not_novarfound)
search_tester("qwertyu=?").claim("No variables found!")
eval_tester = Tester(cool_eval)
eval_tester("= 34+1=").claim("= 35")
eval_tester("= qwer+dfgh=").claim("== dfgh + qwer")
eval_tester("== random()=").claim(True)
eval_tester("random(3)=").claim(True)
symppy_tester = Tester(symppy_eval)
symppy_tester("x-q+3r-2r==").claim("== -q + r + x")
add_tester = Tester(add_line)
add_tester("z=3===").claim("Line saved!")
add_tester("z=[]===").claim("Line saved!")
add_tester("z.append(3)===").claim("Line saved!")