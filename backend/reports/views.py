from django.db.models import BigIntegerField, Sum, Avg, Count, Q, Subquery, OuterRef, IntegerField, DecimalField, Value
from django.db.models.functions import Coalesce
from rest_framework import generics, status
from rest_framework.response import Response
from invoices.models import Invoice, InvoiceItem
from inventory.models import Product, StockMovement
from .serializers import SalesSummarySerializer, TopSellingSerializer, SalesByDaySerializer, SalesByDayQuerySerializer, SalesSummaryQuerySerializer
from .filters import ReportsPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.filters import OrderingFilter, SearchFilter
from .services import get_sales_by_day
from dj_rest_auth.jwt_auth import JWTCookieAuthentication



# Create your views here.

class SalesSummaryAPIView(generics.GenericAPIView):
    serializer_class = SalesSummarySerializer
    queryset = Invoice.objects.all()
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTCookieAuthentication]

    
    
    def get(self, request, *args, **kwargs):
        params = SalesSummaryQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        start = params.validated_data.get('start_date')
        stop = params.validated_data.get('end_date')
        qs = self.get_queryset()
        if start is not None:
            qs = qs.filter(created_at__date__gte=start)
        if stop is not None:
            qs = qs.filter(created_at__date__lte=stop)

        data = qs.aggregate(
            average_invoice=Coalesce(Avg('total_amount'), Value(0), output_field=DecimalField(max_digits=30, decimal_places=2)),
            invoice_count=Count('id'), # didnt use coalesce because count never returns null
            total_revenue=Coalesce(Sum('total_amount'), Value(0), output_field=BigIntegerField()),
        )
        
        serializer = self.get_serializer(instance=data)
        return Response(data={
            'start_date': start,
            'end_date': stop,
            'result': serializer.data}, status=status.HTTP_200_OK)
    

class TopSellingListAPIView(generics.ListAPIView):
    serializer_class = TopSellingSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name', 'sku']
    ordering_fields = ['stock_sold', 'revenue']
    ordering = ['-revenue']
    pagination_class = ReportsPagination
    authentication_classes = [JWTCookieAuthentication]


    def get_queryset(self):
        
        start_date = getattr(self, 'start_date', None)
        end_date = getattr(self, 'end_date', None)
        
        stock_sold_qs = StockMovement.objects.filter(
            product_id=OuterRef('pk'), move_type=StockMovement.TypeChoices.MOVE_OUT
        )

        revenue_qs = InvoiceItem.objects.filter(
            product_id=OuterRef('pk')
        )

        if start_date is not None:
            stock_sold_qs = stock_sold_qs.filter(created_at__date__gte=start_date)
            revenue_qs = revenue_qs.filter(invoice__created_at__date__gte=start_date)
        if end_date is not None:
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

        params = SalesSummaryQuerySerializer(data=self.request.query_params)
        params.is_valid(raise_exception=True)

        queryset = self.filter_queryset(self.get_queryset())

        start_date = params.validated_data.get('start_date')
        end_date = params.validated_data.get('end_date')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            self.paginator.start_date = start_date
            self.paginator.end_date = end_date
            response = self.get_paginated_response(serializer.data)
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class SalesByDayAPIView(generics.ListAPIView):
    serializer_class = SalesByDaySerializer
    pagination_class = ReportsPagination
    queryset = Invoice.objects.none()
    permission_classes = [IsAdminUser]
    authentication_classes = [JWTCookieAuthentication]


    def list(self, request, *args, **kwargs):
        params = SalesByDayQuerySerializer(data=request.query_params)
        params.is_valid(raise_exception=True)
        
        start_date = params.validated_data['start_date']
        end_date = params.validated_data['end_date']

        results = get_sales_by_day(start_date=start_date, end_date=end_date)
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            self.paginator.start_date = start_date
            self.paginator.end_date = end_date
            response = self.get_paginated_response(serializer.data)
            return response

        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
