from functools import wraps
import inspect

def coerce_types(func):
    sig = inspect.signature(func)
    @wraps(func)
    def wrapper(*args, **kwargs):
        bound = sig.bind(*args, **kwargs)
        bound.apply_defaults()
        for name, value in bound.arguments.items():
            expected_type = sig.parameters[name].annotation
            if isinstance(value, expected_type): continue
            elif value is None:
                if sig.parameters[name].default == inspect.Parameter.empty: continue
                bound.arguments[name] = sig.parameters[name].default
            elif expected_type is inspect.Parameter.empty: continue
            else: bound.arguments[name] = expected_type(value)
        return func(*bound.args, **bound.kwargs)
    return wrapper