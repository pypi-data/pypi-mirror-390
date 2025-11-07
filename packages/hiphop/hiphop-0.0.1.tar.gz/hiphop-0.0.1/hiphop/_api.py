import sys

_API_REGISTRY = {}

def export(*names):
    """Register a function/class to one or more API paths."""
    def decorator(obj):
        for name in names:
            _API_REGISTRY[name] = obj
        return obj
    return decorator

def build_api(module_name="hiphop"):
    """Dynamically create public symbols in hiphop/__init__.py."""
    mod = sys.modules[module_name]
    for name, obj in _API_REGISTRY.items():
        parts = name.split(".")
        current = mod
        for part in parts[:-1]:
            current = getattr(current, part, None) or _make_submodule(current, part)
        setattr(current, parts[-1], obj)

def _make_submodule(parent, name):
    import types
    mod = types.ModuleType(name)
    setattr(parent, name, mod)
    return mod
