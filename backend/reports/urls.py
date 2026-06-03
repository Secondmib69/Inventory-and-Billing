from django.urls import path
from .views import *


app_name = 'reports'

urlpatterns = [
    path('sales-summary/', SalesSummaryAPIView.as_view(), name='sales_summary'),
    path('top-selling-products/', TopSellingListAPIView.as_view(), name='top_selling_products'),
    path('sales-by-day/', SalesByDayAPIView.as_view(), name='sales_by_day')
]