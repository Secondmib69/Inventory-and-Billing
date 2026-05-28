from django.shortcuts import render
from .models import *
from .serializers import ProductSeralizer, StockMovementSerializer
from rest_framework import generics

# Create your views here.



class ProductListAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSeralizer
    queryset = Product.objects.order_by('-created_at')



class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSeralizer
    queryset = Product.objects.all()
    lookup_url_kwarg = 'id'
        


class StockMovementsListAPIView(generics.ListCreateAPIView):
    queryset = StockMovement.objects.select_related('product')
    serializer_class = StockMovementSerializer