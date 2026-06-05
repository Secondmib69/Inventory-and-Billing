from django.shortcuts import get_object_or_404
from rest_framework import generics
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer
from django.http import FileResponse
from rest_framework.views import APIView
from .pdf_utils import generate_invoice_pdf
from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .filters import InvoiceFilter, InvoicePagination
from rest_framework.permissions import IsAuthenticated
from dj_rest_auth.jwt_auth import JWTCookieAuthentication
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from config.openapi import (
    TAG_INVOICES,
    cursor_param,
    invoice_filter_params,
    path_id_param,
    search_param,
)


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_INVOICES],
        summary='List invoices',
        description=(
            'Returns a cursor-paginated list of invoices with nested line items. '
            'Authenticated users only.'
        ),
        parameters=[
            search_param('invoice_number', 'customer_name', 'items__product__name'),
            *invoice_filter_params(),
            cursor_param(),
        ],
    ),
    post=extend_schema(
        tags=[TAG_INVOICES],
        summary='Create invoice',
        description=(
            'Create an invoice with line items. Stock is decremented per item and '
            'OUT stock movements are recorded. Fails if any product has insufficient stock. '
            '`invoice_number`, `total_amount`, and `created_at` are set automatically.'
        ),
        request=InvoiceSerializer,
        responses={201: InvoiceSerializer},
    ),
)
class InvoiceListAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTCookieAuthentication]
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


@extend_schema_view(
    get=extend_schema(
        tags=[TAG_INVOICES],
        summary='Retrieve invoice',
        description='Fetch a single invoice with nested line items. Authenticated users only.',
        parameters=[path_id_param('invoice')],
    ),
)
class InvoiceDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTCookieAuthentication]
    serializer_class = InvoiceSerializer
    lookup_url_kwarg = 'id'

    def get_queryset(self):
        qs = Invoice.objects.prefetch_related(
            Prefetch('items', queryset=InvoiceItem.objects.select_related('product'))
        )
        return qs


@extend_schema(
    tags=[TAG_INVOICES],
    summary='Download invoice PDF',
    description=(
        'Generate and download the invoice as a PDF file. '
        'The response is served as an attachment named `{invoice_number}.pdf`.'
    ),
    parameters=[path_id_param('invoice')],
    responses={
        200: OpenApiResponse(
            response=OpenApiTypes.BINARY,
            description='PDF file (`application/pdf`).',
        ),
        404: OpenApiResponse(description='Invoice not found.'),
    },
)
class InvoicePDFDwonloadView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTCookieAuthentication]

    def get(self, request, id):
        invoice = get_object_or_404(Invoice, pk=id)
        pdf_file = generate_invoice_pdf(invoice)

        return FileResponse(
            pdf_file,
            as_attachment=True,
            filename=f'{invoice.invoice_number}.pdf'
        )
