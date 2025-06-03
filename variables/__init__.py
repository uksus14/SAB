from scripts.serializing import Serializers
from typing import Self, Callable, Any
from datetime import datetime
from pathlib import Path

folder = Path(__file__).parent

class Variable[AV]:
    objects: list[Self] = []
    def __new__(cls, name: str, ext: str="json", update: Callable[[Self], Any]=None, serializer: Serializers=None):
        for object in cls.objects:
            if object.name == name: return object
        instance = super().__new__(cls)
        cls.objects.append(instance)
        return instance
    def __init__(self, name: str, ext: str="json", update: Callable[[Self], Any]=None, serializer: Serializers=None):
        self.name = name
        self.path = folder / f"{name}.{ext}"
        self.update = lambda d:d if update is None else update
        self.serializer = Serializers.default() if serializer is None else serializer
        self.data: AV
        self._data: AV = None
        
    @classmethod
    def create(cls, name: str, default: AV, ext: str="json", update: Callable[[Self], Any]=None, serializer: Serializers=None):
        instance = cls(name, ext, update, serializer)
        if instance.path.exists(): instance.refresh()
        else: instance.data = default
        return instance
    def refresh(self):
        with open(self.path, "r", encoding="utf-8") as f:
            self._data = self.serializer.unserialize_func(f.read())
    def __setattr__(self, name: str, value):
        if name not in ["data", "_data"]: return super().__setattr__(name, value)
        super().__setattr__("data", value)
        super().__setattr__("_data", value)
        if name == "_data": return
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(self.serializer.serialize_func(self.data))
    def __repr__(self):
        return f"Variable({self.name}, {self.data})"
    @classmethod
    def do_updates(cls):
        for object in cls.objects:
            if object.update is None: continue
            object.update(object)


USD2KGSVar = Variable[list[dict[str, float|datetime]]]
HistoryVar = Variable[list[dict[str, str|datetime]]]
AccessVar = Variable[list[dict[str, datetime|str]]]
EvalStrVar = Variable[list[str]]