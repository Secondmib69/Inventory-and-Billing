from django.shortcuts import render
from .models import *
from .serializers import ProductSeralizer, StockMovementSerializer
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter, ProductPagePagination, StockMovementPagination

# Create your views here.



class ProductListAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSeralizer
    queryset = Product.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name', 'sku']
    filterset_class = ProductFilter
    ordering_fields = ['created_at', 'updated_at', 'price', 'stock']
    ordering = ['-created_at']
    pagination_class = ProductPagePagination


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSeralizer
    queryset = Product.objects.all()
    lookup_url_kwarg = 'id'
        

class StockMovementsListAPIView(generics.ListCreateAPIView):
    queryset = StockMovement.objects.select_related('product')
    serializer_class = StockMovementSerializer
    pagination_class = StockMovementPagination