from pipeco.contracts import Step

_REGISTRY: dict[str, type[Step]] = {}
def register(name: str):
    def _wrap(cls: type[Step]) -> type[Step]:
        _REGISTRY[name] = cls
        cls.name = name  # convenience
        return cls
    return _wrap

def get_step(name: str) -> type[Step]:
    if name not in _REGISTRY:
        raise KeyError(f"Step '{name}' not registered")
    return _REGISTRY[name]
