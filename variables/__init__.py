from scripts.serializing import Serializers
from typing import Self, Callable, Any
from datetime import datetime
from pathlib import Path

folder = Path(__file__).parent

class Variable[AV]:
    objects: list[Self] = []
    def __new__(cls, name: str, *args, **kwargs):
        for object in cls.objects:
            if object.name == name: return object
        instance = super().__new__(cls)
        cls.objects.append(instance)
        return instance
    def __init__(self, name: str, ext: str="json", update: Callable[[Self], Any]|None=None, serializer: Serializers|None=None):
        self.name = name
        self.path = folder / f"{name}.{ext}"
        if update is None: update = lambda var:None
        self.update = lambda: update(self)
        self.serializer = Serializers.default() if serializer is None else serializer
        self.data: list[AV]
        self._data: list[AV]|None = None
        
    @classmethod
    def create(cls, name: str, default: list[AV]|None=None, ext: str="json", update: Callable[[Self], Any]|None=None, serializer: Serializers|None=None):
        instance = cls(name, ext, update, serializer)
        if instance.path.exists(): instance.refresh()
        else: instance.data = default or []
        instance.update()
        return instance
    def append(self, item: Any):
        self.data += [item]
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
            object.update()


from typing import TypedDict
USD2KGSEntry = TypedDict('USD2KGSEntry', {"time": datetime, "rate": float})
HistoryEntry = TypedDict('HistoryEntry', {"query": str, "time": datetime})
AccessEntry = TypedDict('AccessEntry', {"call": str, "time": datetime})

USD2KGSVar = Variable[USD2KGSEntry]
HistoryVar = Variable[HistoryEntry]
AccessVar = Variable[AccessEntry]
EvalStrVar = Variable[str]