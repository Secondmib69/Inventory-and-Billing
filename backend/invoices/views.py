from django.shortcuts import render
from rest_framework import generics
from .models import Invoice
from .serializers import InvoiceSerializer

# Create your views here.


class InvoiceListAPIView(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer