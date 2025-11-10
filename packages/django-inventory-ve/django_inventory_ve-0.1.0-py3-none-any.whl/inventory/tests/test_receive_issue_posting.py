import pytest
from decimal import Decimal
from finacc.models.company import Company
from finacc.models.accounts import Account
from inventory.models.warehouse import Warehouse
from inventory.models.item import StockItem
from inventory.models.move import StockMove
from inventory.models.config import InventoryAccountMapping
from inventory.enums import MoveType
from inventory.posting.adapters import receive_stock, issue_stock


@pytest.mark.django_db
def test_receive_then_issue_posts_to_finacc():
    c = Company.objects.create(name="ACME")
    wh = Warehouse.objects.create(company=c, code="MAIN", name="Main")
    item = StockItem.objects.create(company=c, sku="PRD-001", name="Widget", uom="pcs")
    asset = Account.objects.create(company=c, code="1100", name="Inventory", kind="asset", normal_balance="debit")
    cogs = Account.objects.create(company=c, code="5000", name="COGS", kind="expense", normal_balance="debit")
    adj = Account.objects.create(company=c, code="2109", name="Inv Adjust", kind="liability", normal_balance="credit")
    InventoryAccountMapping.objects.create(company=c, inventory_asset=asset, cogs=cogs, inventory_adjustment=adj)


    m_in = StockMove.objects.create(company=c, item=item, warehouse=wh, date="2025-11-09", currency="INR", type=MoveType.IN.value, qty=Decimal("10"), unit_cost=Decimal("250"), ref="B-1")
    e1 = receive_stock(m_in)
    assert e1.is_posted


    m_out = StockMove.objects.create(company=c, item=item, warehouse=wh, date="2025-11-09", currency="INR", type=MoveType.OUT.value, qty=Decimal("2"), unit_cost=Decimal("0"), ref="S-1")
    e2 = issue_stock(m_out)
    assert e2.is_posted