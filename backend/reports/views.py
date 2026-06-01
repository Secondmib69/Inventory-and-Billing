from django.shortcuts import render
from django.db.models import BigIntegerField, Sum, Avg, Count, Prefetch, Q, Subquery, OuterRef, IntegerField, DecimalField, Value
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework.response import Response
from invoices.models import Invoice, InvoiceItem
from inventory.models import Product, StockMovement
from .serializers import SalesSummarySerializer, TopSellingSerializer
from .filters import CustomDateFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, DateFilter
from rest_framework.filters import OrderingFilter, SearchFilter


# Create your views here.

class SalesSummaryAPIView(generics.GenericAPIView):
    serializer_class = SalesSummarySerializer
    queryset = Invoice.objects.all()
    filter_backends = [DjangoFilterBackend]
    filterset_class = CustomDateFilter
    
    
    def get(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset())
        data = qs.aggregate(
            average_invoice=Coalesce(Avg('total_amount'), Value(0), output_field=DecimalField(max_digits=30, decimal_places=2)),
            invoice_count=Count('id'), # didnt use coalesce because count never returns null
            total_revenue=Coalesce(Sum('total_amount'), Value(0), output_field=BigIntegerField()),
        )
        start = request.query_params.get('created_at_after')
        stop = request.query_params.get('created_at_before')
        
        serializer = self.get_serializer(instance=data)
        return Response(data={
            'created_at_after': start,
            'created_at_before': stop,
            'result': serializer.data}, status=status.HTTP_200_OK)
    

class TopSellingListAPIView(generics.ListAPIView):
    serializer_class = TopSellingSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'sku']
    ordering_fields = ['stock_sold', 'revenue']
    ordering = ['-revenue']


    def get_queryset(self):
        
        stock_sold_qs = StockMovement.objects.filter(
            product_id=OuterRef('pk'), move_type=StockMovement.TypeChoices.MOVE_OUT
        )

        revenue_qs = InvoiceItem.objects.filter(
            product_id=OuterRef('pk')
        )

        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')


        if start_date:
            stock_sold_qs = stock_sold_qs.filter(created_at__date__gte=start_date)
            revenue_qs = revenue_qs.filter(invoice__created_at__date__gte=start_date)
        if end_date:
            stock_sold_qs = stock_sold_qs.filter(created_at__date__lte=end_date)
            revenue_qs = revenue_qs.filter(invoice__created_at__date__lte=end_date)

        stock_sold_subquery = stock_sold_qs.values('product_id').annotate(total=Sum('quantity')).values('total')[:1] # subquery should only return 1 row
        revenue_subquery = revenue_qs.values('product_id').annotate(total=Sum('item_total_price')).values('total')[:1] # subquery should only return 1 row


        qs = Product.objects.annotate(stock_sold=
            Coalesce(
                Subquery(stock_sold_subquery),
                Value(0),
                output_field=IntegerField()
            ),
            revenue=Coalesce(
                Subquery(revenue_subquery),
                Value(0),
                output_field=BigIntegerField()
            )
        )

        return qs
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            # Add metadata to paginated response
            response.data['start_date'] = self.request.query_params.get('start_date')
            response.data['end_date'] = self.request.query_params.get('end_date')
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'start_date': self.request.query_params.get('start_date'),
            'end_date': self.request.query_params.get('end_date'),
            'results': serializer.data
        })

