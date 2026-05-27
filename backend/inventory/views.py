from django.shortcuts import render
from .models import *
from .serializers import ProductSeralizer, StockMovementSerializer
from rest_framework import generics

# Create your views here.



class ProductListAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSeralizer
    queryset = Product.objects.order_by('-created_at')

    # def get_queryset(self):
    #     qs = Product.objects.all()
    #     given_pk = self.request.query_params.get('pk')
    #     if given_pk:
    #         return qs.filter(pk=given_pk)
    #     return qs
        


class StockMovementsListAPIView(generics.ListCreateAPIView):
    queryset = StockMovement.objects.all()
    serializer_class = StockMovementSerializer