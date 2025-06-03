from scripts.serializing import Serializers
from typing import Self, Callable, Any
from datetime import datetime
from pathlib import Path
import json

folder = Path(__file__).parent

class Variable[AV]:
    objects: list[Self] = []
    def __new__(cls, name: str):
        for object in cls.objects:
            if object.name == name: return object
        instance = super().__new__(cls)
        cls.objects.append(instance)
        return instance
    def __init__(self, name: str):
        self.name = name
        self.path = folder / f"{name}.json"
        self.data: AV
        self.update: Callable[[Self], Any]|None
        self._data: AV = None
        
    @classmethod
    def create(cls, name: str, default: AV, update: Callable[[Self], Any]=None):
        instance = cls(name)
        if instance.path.exists():
            with open(instance.path, "r", encoding="utf-8") as f:
                instance._data = Serializers.unserialize(json.loads(f.read()))
        else: instance.data = default
        if instance.data == None: instance.data = default
        instance.update = update
        return instance
    def __setattr__(self, name: str, value):
        if name not in ["data", "_data"]: return super().__setattr__(name, value)
        super().__setattr__("data", value)
        super().__setattr__("_data", value)
        if name == "_data": return
        with open(self.path, "w", encoding="utf-8") as f:
            f.write(json.dumps(Serializers.serialize(self.data), ensure_ascii=False))
    def __repr__(self):
        return f"Variable({self.name}, {self.data})"
    @classmethod
    def do_updates(cls):
        for object in cls.objects:
            if object.update is None: continue
            object.update(object)