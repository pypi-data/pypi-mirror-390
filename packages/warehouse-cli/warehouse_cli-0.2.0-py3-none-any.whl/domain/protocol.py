from typing import Protocol, Dict

class Warehouse(Protocol):
    def add(self, item: Dict):
        ...

    def delete(self, item_id: int):
        ...

    def edit(self, item_id: int, replace_item: Dict):
        ...

    def search(self, query: str):
        ...

    def list(self):
        ...