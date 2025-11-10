from rest_framework import serializers
from inventory.models.item import StockItem
from inventory.models.warehouse import Warehouse
from inventory.models.move import StockMove


class WarehouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Warehouse
        fields = "__all__"


class StockItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockItem
        fields = "__all__"


class StockMoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockMove
        fields = ["company", "item", "warehouse", "date", "currency", "type", "qty", "unit_cost", "ref", "memo"]