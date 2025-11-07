import click
from rich.console import Console
from rich.table import Table
from domain.product import ProductId
import pyfiglet
from domain.protocol import Warehouse
from infrastructure.factory import factory
import infrastructure.json_backend

console = Console()


def show_banner():
    banner = pyfiglet.figlet_format("Warehouse CLI", font="slant")
    console.print(f"[bold cyan]{banner}[/bold cyan]")


def show_inventory(items):
    table = Table(title="📦 Inventory", header_style="bold magenta")
    table.add_column("ID", justify="right", style="bold yellow")
    table.add_column("Name", style="white")
    table.add_column("Price", justify="right", style="green")
    table.add_column("Qty", justify="center", style="bright_blue")

    for item in items:
        table.add_row(
            str(item["id"]), item["name"], f"${item['price']}", str(item["quantity"])
            )

    console.print(table)

class FancyGroup(click.Group):
    def get_help(self, ctx):
        show_banner()
        help_text = super().get_help(ctx)
        console.print(f"[bold white]{help_text}[/bold white]")
        return ""

class WarehouseCLI:

    def __init__(self, backend="json"):
        self.backend_name = backend
        self.warehouse: Warehouse = factory.create(backend)

    def run(self):
        @click.group(cls=FancyGroup, invoke_without_command=True)
        @click.option(
            "--backend",
            type=click.Choice(factory.available(), case_sensitive=False),
            default=self.backend_name,
            help="Choose warehouse backend"
        )
        @click.pass_context
        def cli(ctx, backend):
            ctx.obj = self
            if ctx.invoked_subcommand is None:
                console.clear()
                show_banner()
                console.print(f"🚀 Using backend: [bold green]{backend}[/]")
                console.print(
                    "[yellow]Use '--help' to see available commands[/yellow]"
                    )


        @cli.command()
        @click.pass_context
        def list(ctx):
            """List all products"""
            self.show_list()

        @cli.command()
        @click.pass_context
        def summary(ctx):
            """List all products"""
            self.show_summary()

        @cli.command()
        @click.pass_context
        @click.option("--name", prompt="Product name")
        @click.option("--price", type=float, prompt="Price")
        @click.option("--quantity", type=int, prompt="Quantity")
        def add(ctx, name, price, quantity):
            """Add a new product"""
            self.add_item(name, price, quantity)

        @cli.command()
        @click.pass_context
        @click.option("--id", type=int, prompt="Product ID to edit")
        @click.option("--name", prompt="New product name")
        @click.option("--price", type=float, prompt="Price")
        @click.option("--quantity", type=int, prompt="Quantity")
        def edit(ctx, id, name, price, quantity):
            """Edit an existing product"""
            self.edit_item(id, name, price, quantity)

        @cli.command()
        @click.pass_context
        @click.option("--query", prompt="Search query")
        def search(ctx, query):
            """Search products by name"""
            self.search_item(query)

        @cli.command()
        @click.pass_context
        @click.option("--id", type=int, prompt="Product ID to delete")
        def delete(ctx, id):
            """Delete a product by ID"""
            self.delete_item(id)

        cli()


    def show_list(self):
        items = self.warehouse.list()
        if not items:
            console.print("🟡 No products found.")
        else:
            show_inventory(items)


    def show_summary(self):
        items = self.warehouse.list()

        if not items:
            console.print("🟡 No products found.")
            return

        total_items = len(items)
        total_quantity = sum(i["quantity"] for i in items)
        total_value = sum(i["price"] * i["quantity"] for i in items)

        table = Table(title="📊 Warehouse Summary", header_style="bold cyan")
        table.add_column("Metric", style="bold yellow")
        table.add_column("Value", style="white", justify="right")

        table.add_row("Total Products", str(total_items))
        table.add_row("Total Quantity", str(total_quantity))
        table.add_row("Total Inventory Value", f"${total_value}")

        console.print(table)

    def add_item(self, name: str, price: float, quantity: int):
        next_id = len(self.warehouse.list()) + 1
        item_data = {
            "id": ProductId(next_id),
            "name": name,
            "price": price,
            "quantity": quantity
        }
        success, msg = self.warehouse.add(item_data)
        console.print(msg)

    def edit_item(self, item_id: int, name: str, price: float, quantity: int):
        new_item = {
            "id": ProductId(item_id),
            "name": name,
            "price": price,
            "quantity": quantity
        }
        success, msg = self.warehouse.edit(item_id, new_item)
        console.print(msg)

    def search_item(self, query: str):
        items = self.warehouse.search(query)
        if not items:
            console.print("🟡 No products found.")
        else:
            show_inventory(items)

    def delete_item(self, item_id: int):
        removed = self.warehouse.delete(item_id)
        if removed:
            console.print(f"❌ Deleted product with ID {item_id}")
        else:
            console.print(f"🟡 Product ID {item_id} not found")


def cli():
    WarehouseCLI().run()