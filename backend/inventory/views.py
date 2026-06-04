from django.shortcuts import render
from .models import *
from .serializers import ProductSeralizer, StockMovementSerializer
from rest_framework import generics
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .filters import ProductFilter, ProductPagePagination, StockMovementPagination
from rest_framework.permissions import IsAdminUser
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from .permissions import IsAdminOrAuthenticatedReadonly
from drf_spectacular.utils import OpenApiParameter,extend_schema


# Create your views here.



class ProductListAPIView(generics.ListCreateAPIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAdminOrAuthenticatedReadonly]
    serializer_class = ProductSeralizer
    queryset = Product.objects.all()
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['name', 'sku']
    filterset_class = ProductFilter
    ordering_fields = ['created_at', 'updated_at', 'price', 'stock']
    ordering = ['-created_at']
    pagination_class = ProductPagePagination


class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    authentication_classes = [JWTCookieAuthentication]
    permission_classes = [IsAdminOrAuthenticatedReadonly]
    serializer_class = ProductSeralizer
    queryset = Product.objects.all()
    lookup_url_kwarg = 'id'
        

class StockMovementsListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTCookieAuthentication]
    queryset = StockMovement.objects.select_related('product')
    serializer_class = StockMovementSerializer
    pagination_class = StockMovementPagination