from typing import Any, Self
import regex

class Message:
    objects: dict[str, Self] = {}
    def __init__(self, name: str, pattern_temp: str, template: str=None):
        self.name = name
        if template is None:
            template = regex.sub(r"\\(.)", r"\1", regex.sub(r"\(\?P<(\w+)>[^)]+\)", r"{\1}", pattern_temp))
        self.pattern = f"^{pattern_temp}$"
        self.template = template
        self.objects[name] = self
    def match(self, call: str) -> dict[str, str]|None:
        match = regex.match(self.pattern, call) if isinstance(call, str) else None
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
        if not isinstance(next(iter(self), True), Message):
            self.messages = {name: Message(name, message) for name, message in self.messages.items()}
    @classmethod
    def all(cls) -> Self:
        return cls(**Message.objects)
    @property
    def patterns(self):
        return [message.pattern for message in self]
    @property
    def templates(self):
        return [message.template for message in self]
    def match(self, call: str) -> Message|None:
        for message in self:
            res = message.match(call)
            if res is not None: return message
        return None
    def __iter__(self):
        for message in self.messages.values():
            yield message
    def __repr__(self) -> str:
        return f"MessageList({', '.join(map(str, self))})"
    def __getattribute__(self, name: str) -> Any|Message:
        message = super().__getattribute__('messages').get(name, None)
        return message if message is not None else super().__getattribute__(name)