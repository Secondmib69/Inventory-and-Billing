from django.urls import path
from .views import *


app_name = 'inventory'

urlpatterns = [
    path('products/', PostListAPIView.as_view(), name='product_list')
]