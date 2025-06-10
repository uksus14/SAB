from typing import Self
import regex

class Message:
    objects: dict[str, Self] = {}
    def __init__(self, name: str, pattern_temp: str, template: str=None):
        self.name = name
        if template is None:
            recursive = lambda p: fr"\{p[0]}((?>[^{p}]+|(?R))*)\{p[1]}"
            template = regex.sub(r"\(\?P<(?P<name>\w+)>[^()]*"+recursive("()")+"[^()]*\)", r"{\g<name>}", pattern_temp)
            template = regex.sub(r"\\(.)", r"\1", template)
        self.pattern = f"^{pattern_temp}$"
        self.template = template
        self.objects[name] = self
    def match(self, call: str) -> dict[str, str]|None:
        match = regex.match(f"^{self.pattern}$", call) if isinstance(call, str) else None
        return match.groupdict() if match is not None else None
    def format(self, **kwargs):
        return self.template.format(**kwargs)
    def __repr__(self) -> str:
        return f"Message({self.name}, {self.pattern}, {self.template})"
    def __str__(self) -> str:
        return self.template

class MessageList:
    def __init__(self, **messages: Message|str):
        self.messages = messages
        if isinstance(next(iter(self), None), Message): return
        self.messages = {name: Message(name, message) for name, message in self.messages.items()}
    @classmethod
    def all(cls) -> Self:
        return cls(**Message.objects)
    def match(self, call: str) -> Message|None:
        for message in self:
            res = message.match(call)
            if res is not None: return message
        return None
    def __iter__(self):
        return iter(self.messages.values())
    def __repr__(self) -> str:
        return f"MessageList({', '.join(map(str, self))})"
    def __getattr__(self, name: str) -> Message:
        return self.messages.get(name)