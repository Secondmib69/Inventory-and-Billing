from django.urls import path
from .views import *


app_name = 'inventory'

urlpatterns = [
    path('products/', ProductListAPIView.as_view(), name='product_list'),
    path('products/<int:id>/', ProductDetailAPIView.as_view(), name='product_detail'),
    path('stock-movements/', StockMovementsListAPIView.as_view(), name='stock_movement_list')
]