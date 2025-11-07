from typing import Dict
from infrastructure.factory import factory
from domain.product import Product, ProductId
from pathlib import Path
from pydantic import ValidationError
import json

@factory.register('json')
class JSONWarehouse:

    def __init__(self, path: str = 'data.json'):
        self.path = Path(path)
        self.path.touch(exist_ok=True)

    def _load(self):
            text = self.path.read_text()
            if not text.strip():
                return []
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                self.path.write_text('[]')
                return []

    def _save(self, data):
        self.path.write_text(json.dumps(data, indent=2))

    def add(self, item: dict) -> tuple[bool, str]:
        try:
            product = Product(**item)
            data = self._load()
            if not product.id:
                product.id = ProductId(len(data) + 1)
            data.append(product.to_dict())
            self._save(data)
            return (
                True,
                f"✅ Added [bold green]{product.name}[/]"
                f"💲{product.price} × {product.quantity} (ID: {product.id.id})"
                )
        except ValidationError as e:
            error_messages = "\n".join(f"- {err['msg']}" for err in e.errors())
            return (
                False,
                f"⚠️ [bold yellow]Invalid input![/]\n[white]{error_messages}[/white]"
                )


    def delete(self, item_id):
        data = [i for i in self._load() if i['id'] != item_id]
        success = next((i for i in self._load() if i['id'] == item_id), None)
        if success:
            self._save(data)
            return True
        return False
    def edit(self, item_id, replace_item: Product):
        data = self._load()
        item = next((i for i in data if i['id'] == item_id), None)
        if item:
            try:
                product = Product(**replace_item)
                item.update({
                        "id" : item_id,
                        "name": replace_item["name"],
                        "price": replace_item["price"],
                        "quantity": replace_item["quantity"]
                })
                self._save(data)
                return (
                    True, 
                    f"✏️ Edited product [bold green]{product.name}[/] (ID: {item_id})"
                )
            except:
                return (
                    False,
                    "⚠️ Invalid input! Please check name, price, and quantity."
                    )
        
        else:
            return False, f"⚠️ Product with ID {item_id} not found."
            
    def search(self, query):
        return [
            i for i in self._load()
            if query.lower() in i['name'].lower()
        ]

    def list(self):
        return self._load()