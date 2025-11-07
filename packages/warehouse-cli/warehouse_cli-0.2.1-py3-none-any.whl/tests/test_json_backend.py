import unittest
from unittest.mock import patch, mock_open, MagicMock
from pathlib import Path
import json

from domain.product import Product, ProductId
from infrastructure.json_backend import JSONWarehouse
from infrastructure.factory import factory


class TestJSONWarehouse(unittest.TestCase):

    def setUp(self):
        self.temp_file = "test_data.json"
        self.warehouse = JSONWarehouse(path=self.temp_file)
        self.addCleanup(lambda: Path(self.temp_file).unlink(missing_ok=True))

    def test_add_product_successful(self):
        success, msg = self.warehouse.add({
            "name": "laptop", "price": 5000000, "quantity": 2
        })
        self.assertTrue(success)
        self.assertIn("Added", msg)
        self.assertEqual(len(self.warehouse.list()), 1)

    def test_add_product_validation_error(self):
        success, msg = self.warehouse.add({
            "name": "ab", "price": -100, "quantity": 0
        })
        self.assertFalse(success)
        self.assertIn("at least 3 character", msg)
        self.assertIn("positive number", msg)     
        self.assertIn("not negative number", msg)

    def test_edit_existing_item(self):
        self.warehouse.add({"name": "phone", "price": 2000000, "quantity": 1})
        
        success, msg = self.warehouse.edit(1, {
            "name": "samsung phone", "price": 2500000, "quantity": 3
        })
        self.assertTrue(success)
        self.assertIn("Edited", msg)

        item = self.warehouse.list()[0]
        self.assertEqual(item["name"], "samsung phone")
        self.assertEqual(item["quantity"], 3)

    def test_edit_non_existing_item(self):
        success, msg = self.warehouse.edit(999, {
            "name": "test", "price": 1000, "quantity": 1
        })
        self.assertFalse(success)
        self.assertIn("not found", msg)

    def test_delete_existing_item(self):
        self.warehouse.add({"name": "mouse", "price": 500000, "quantity": 1})
        removed = self.warehouse.delete(1)
        self.assertTrue(removed)
        self.assertEqual(len(self.warehouse.list()), 0)

    def test_delete_non_existing_item(self):
        removed = self.warehouse.delete(999)
        self.assertFalse(removed)

    @patch("pathlib.Path.read_text")
    def test_corrupted_file(self, mock_read):
        mock_read.return_value = "Error"
        warehouse = JSONWarehouse(path=self.temp_file)
        self.assertEqual(warehouse.list(), [])

    def test_factory_register(self):
        self.assertIn("json", factory.available())
        instance = factory.create("json")
        self.assertIsInstance(instance, JSONWarehouse)
