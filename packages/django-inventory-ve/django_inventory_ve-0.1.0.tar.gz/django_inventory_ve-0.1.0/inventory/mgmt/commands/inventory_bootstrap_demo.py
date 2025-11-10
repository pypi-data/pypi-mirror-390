from django.core.management.base import BaseCommand
from finacc.models.company import Company
from finacc.models.accounts import Account
from inventory.models.warehouse import Warehouse
from inventory.models.item import StockItem
from inventory.models.config import InventoryAccountMapping


class Command(BaseCommand):
    help = "Create demo warehouse, items, and inventory account mapping"


def add_arguments(self, parser):
    parser.add_argument("--company", type=int, required=True)


def handle(self, *args, **opts):
    c = Company.objects.get(id=opts["company"])
    wh, _ = Warehouse.objects.get_or_create(company=c, code="MAIN", defaults={"name": "Main Warehouse"})
    StockItem.objects.get_or_create(company=c, sku="PRD-001", defaults={"name": "Widget", "uom": "pcs", "cost_method": "avg"})
    StockItem.objects.get_or_create(company=c, sku="PRD-002", defaults={"name": "Gadget", "uom": "pcs", "cost_method": "avg"})
    def acc(code): return Account.objects.get(company=c, code=code)
    InventoryAccountMapping.objects.get_or_create(company=c, defaults={
        "inventory_asset": acc("1100"),
        "cogs": acc("5000"),
        "inventory_adjustment": acc("2000"),
    })
    self.stdout.write(self.style.SUCCESS("Inventory demo data ready"))