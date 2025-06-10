from scripts.utils import all_ways, pattern_or
from scripts.actions import Action

class Code[AC](Action[AC]):
    order = -1
    _list = []
    def __init__(self, value: AC, *codes: str, code_pattern: str="{code}"):
        self.value = value
        self.codes = all_ways(*codes)
        self.code_pattern = code_pattern
        codes = pattern_or(*self.codes)
        pattern = codes if code_pattern is None else code_pattern.format(code=codes)
        super().__init__(self.getter, pattern=pattern or codes)
    def getter(self, call: str, **kwargs) -> AC:
        return self.value.format(**kwargs) if isinstance(self.value, str) else self.value
    def match(self, call: str) -> dict[str, str]|None:
        if self.code_pattern != "{code}": return super().match(call)
        return {} if call in self.codes else None
    @classmethod
    def resolve(cls, call: str) -> AC|None:
        return super().resolve(call.lower())