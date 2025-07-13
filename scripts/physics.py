class Dimension:
    dims = {}
    def __init__(self, symbol: str):
        self.dims[symbol] = self
        
class Physics:
    def __init__(self, num: float, units: dict['Unit', float]):
        self.num = num
        self.units = units
    def __repr__(self):
        return f"{self.num} {self.dimentions(self.units)}"
    def __str__(self):
        return f"{self.num} {self.units}"
    def __add__(self, other):
        if isinstance(other, Physics) and self.units == other.units:
            return Physics(self.num + other.num, self.units)
        raise ValueError("Cannot add different dimensions")
    def __sub__(self, other):
        if isinstance(other, Physics) and self.units == other.units:
            return Physics(self.num - other.num, self.units)
        raise ValueError("Cannot subtract different dimensions")
class Unit:
    units: dict[str, Self] = {}
    miltiples: dict[Self, list[Self]] = {}
    math_methods = ['add', 'radd', 'sub', 'rsub', 'mul', 'rmul', 'truediv', 'rtruediv', 'rpow', 'floordiv', 'rfloordiv', 'mod', 'rmod']
    def __new__(cls, name: str, symbol: str, dimantions: Physics=None):
        if symbol not in cls.units:
            cls.units[symbol] = super().__new__(cls)
            if dimantions.dims
        return cls.units[symbol]
    def __init__(self, name: str, symbol: str, dimantions: Physics=None):
        self.name = name
        self.symbol = symbol
        self.math = dimantions if dimantions else Physics(1, symbol)
        for dunder in self.math_methods:
            dunder = f"__{dunder}__"
            setattr(self, dunder, getattr(self.math, dunder))
    def __pow__(self, power: int) -> Physics:
        if isinstance(power, int):
            return Physics(self.math.num ** power, self.math.units ** power)
        raise ValueError("Power must be an integer")
    def fit(self, value: Physics) -> Physics:
        for dim in self.value.dims:
            if dim
        best_fit = 
        for unit in self.units.values():
            if unit.math:
                return Physics(value.num, unit)
    def __call__(self, value: Physics) -> Physics:
        return 
    def __repr__(self): return f"Unit('{self.name}', '{self.symbol}')"
    def __str__(self): return self.symbol
    def __hash__(self): return hash((self.name, self.symbol))
class Units:
    def __init__(self, units: dict[]):
        self.units = {}
        self.multiples = {}
    def __getitem__(self, key: str) -> Unit:
        return self.units[key]
    def __setitem__(self, key: str, value: Unit):
        self.units[key] = value
    def __contains__(self, key: str) -> bool:
        return key in self.units
    def __iter__(self):
        return iter(self.units.values())
    def __repr__(self): return f"Units({list(self.units.keys())})"

meter = Unit('meter', 'm')
sq_meter = Unit('square meter', dimantions=meter**2)
km = Unit('kilometer', 'km', dimantions=1000*meter)
meter*4000