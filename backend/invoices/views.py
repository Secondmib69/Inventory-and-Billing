from django.shortcuts import render, get_object_or_404
from rest_framework import generics
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer
from django.http import FileResponse
from rest_framework.views import APIView
from .pdf_utils import generate_invoice_pdf
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .filters import InvoiceFilter, InvoicePagination

# Create your views here.


class InvoiceListAPIView(generics.ListCreateAPIView):
    serializer_class = InvoiceSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['invoice_number', 'customer_name', 'items__product__name']
    filterset_class = InvoiceFilter
    pagination_class = InvoicePagination

    def get_queryset(self):
        qs = Invoice.objects.prefetch_related(
            Prefetch(
                'items', queryset=InvoiceItem.objects.select_related('product')
            )
        ).distinct()
        return qs


class InvoiceDetailAPIView(generics.RetrieveAPIView):
    serializer_class = InvoiceSerializer
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        qs = Invoice.objects.prefetch_related(
            Prefetch('items', queryset=InvoiceItem.objects.select_related('product'))
        )
        return qs



class InvoicePDFDwonloadView(APIView):

    def get(self, request, id):
        invoice = get_object_or_404(Invoice, pk=id)
        pdf_file = generate_invoice_pdf(invoice)

        return FileResponse(
            pdf_file,
            as_attachment=True,
            filename= f'{invoice.invoice_number}.pdf'
        )

