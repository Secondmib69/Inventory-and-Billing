from django.shortcuts import render
from .models import *
from .serializers import ProductSeralizer
from rest_framework import generics

# Create your views here.



class PostListAPIView(generics.ListCreateAPIView):
    serializer_class = ProductSeralizer
    queryset = Product.objects.order_by('-created_at')
