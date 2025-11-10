from django.urls import path
from inventory.api.views import WarehouseListCreate, StockItemListCreate, StockMoveCreatePost


urlpatterns = [
    path("warehouses/", WarehouseListCreate.as_view()),
    path("items/", StockItemListCreate.as_view()),
    path("moves/", StockMoveCreatePost.as_view()),
]