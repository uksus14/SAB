from datetime import datetime, timedelta
from typing import Callable, Any, Self
import regex

class Serializers:
    def __init__(self, serialize: Callable[[Any], Any], unserialize: Callable[[Any], Any], raw: bool=False):
        self.serialize_func = serialize
        self.unserialize_func = unserialize
        self.raw = raw
    @classmethod
    def unserialize(cls, data):
        try:
            name, new_data = data
            if regex.match(r"^s_[a-zA-Z0-9_]+$", name) is None: raise Exception
            func = cls.get(name).unserialize_func
        except:
            new_data = data
            func = cls.get(f"s_{type(data).__name__}").unserialize_func
        return func(new_data)
    @classmethod
    def serialize(cls, data):
        name = f"s_{type(data).__name__}"
        ser = cls.get(name)
        if ser.raw: return data
        return [name, ser.serialize_func(data)]
    @classmethod
    def get(cls, type: str) -> Self:
        i = lambda x:x
        return getattr(cls, type, lambda:cls(i, i, raw=True))()
    @classmethod
    def s_datetime(cls):
        serialize = lambda data: data.timestamp()
        unserialize = lambda data: datetime.fromtimestamp(data)
        return cls(serialize, unserialize)
    @classmethod
    def s_timedelta(cls):
        serialize = lambda data: data.total_seconds()
        unserialize = lambda data: timedelta(seconds=data)
        return cls(serialize, unserialize)
    @classmethod
    def s_list(cls):
        serialize = lambda data: [cls.serialize(entry) for entry in data]
        unserialize = lambda data: [cls.unserialize(entry) for entry in data]
        return cls(serialize, unserialize)
    @classmethod
    def s_dict(cls):
        serialize = lambda data: {cls.serialize(key): cls.serialize(value) for key, value in data.items()}
        unserialize = lambda data: {cls.unserialize(key): cls.unserialize(value) for key, value in data.items()}
        return cls(serialize, unserialize)
    @classmethod
    def s_tuple(cls):
        serialize = lambda data: tuple([cls.serialize(entry) for entry in data])
        unserialize = lambda data: tuple([cls.unserialize(entry) for entry in data])
        return cls(serialize, unserialize)