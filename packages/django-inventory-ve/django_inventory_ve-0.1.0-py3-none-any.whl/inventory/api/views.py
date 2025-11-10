from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from inventory.api.serializers import WarehouseSerializer, StockItemSerializer, StockMoveSerializer
from inventory.models.move import StockMove
from inventory.enums import MoveType
from inventory.posting.adapters import receive_stock, issue_stock


class WarehouseListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = WarehouseSerializer(data=request.data); ser.is_valid(raise_exception=True); ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


class StockItemListCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = StockItemSerializer(data=request.data); ser.is_valid(raise_exception=True); ser.save()
        return Response(ser.data, status=status.HTTP_201_CREATED)


class StockMoveCreatePost(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request):
        ser = StockMoveSerializer(data=request.data); ser.is_valid(raise_exception=True)
        mv = ser.save()
        if mv.type == MoveType.IN.value:
            entry = receive_stock(mv)
        elif mv.type == MoveType.OUT.value:
            entry = issue_stock(mv)
        else:
            return Response({"move_id": mv.id, "note": "Transfer posting not implemented"}, status=status.HTTP_201_CREATED)
        return Response({"move_id": mv.id, "journal_entry_id": entry.id}, status=status.HTTP_201_CREATED)