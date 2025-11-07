class WarehouseFactory:
    def __init__(self):
        self._registry = {}

    def register(self, name, cls = None):
        if cls is None:
            def decorator(c):
                self._registry[name] = c
                return c
            return decorator
        self._registry[name] = cls
        return cls

    def create(self, name, **kwargs):
        if name not in self._registry.keys():
            raise ValueError(f"Unknown warehouse: {name}")
        return self._registry[name](**kwargs)
    
    def available(self):
        return list(self._registry.keys())

factory = WarehouseFactory()