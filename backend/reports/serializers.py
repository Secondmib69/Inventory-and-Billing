from rest_framework import serializers
from inventory.models import Product
from invoices.serializers import ProductMiniSerializer
from rest_framework.reverse import reverse


class SalesSummarySerializer(serializers.Serializer):

    average_invoice = serializers.DecimalField(
        max_digits=30,
        decimal_places=2,
        help_text='Mean invoice `total_amount` for the selected period.',
    )
    invoice_count = serializers.IntegerField(
        help_text='Number of invoices in the selected period.',
    )
    total_revenue = serializers.IntegerField(
        help_text='Sum of all invoice `total_amount` values in the selected period.',
    )


class SalesSummaryResponseSerializer(serializers.Serializer):
    start_date = serializers.DateField(
        allow_null=True,
        required=False,
        help_text='Echo of the `start_date` query param, or null when omitted.',
    )
    end_date = serializers.DateField(
        allow_null=True,
        required=False,
        help_text='Echo of the `end_date` query param, or null when omitted.',
    )
    result = SalesSummarySerializer(help_text='Aggregated sales metrics.')


class SalesSummaryQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(
        required=False,
        help_text='Inclusive start date (ISO 8601). Omit to include all history.',
    )
    end_date = serializers.DateField(
        required=False,
        help_text='Inclusive end date (ISO 8601). Omit to include all history.',
    )


class TopSellingSerializer(serializers.ModelSerializer):

    def get_details(self, obj):
        request = self.context.get('request')
        url = reverse(request=request, viewname='inventory:product_detail', kwargs={'id': obj.id})
        return url
    

    details = serializers.SerializerMethodField(
        help_text='URL to the product detail endpoint.',
    )
    stock_sold = serializers.IntegerField(
        help_text='Total OUT stock movement quantity in the requested date range.',
    )
    revenue = serializers.IntegerField(
        help_text='Sum of line-item totals from invoices in the requested date range.',
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'details','stock_sold', 'revenue']


class SalesByDaySerializer(serializers.Serializer):

    day = serializers.DateField(help_text='Calendar date (ISO 8601).')
    revenue = serializers.IntegerField(
        help_text='Total invoice revenue recorded on this day.',
    )


class ReportsPaginatedResponseSerializer(serializers.Serializer):
    start_date = serializers.DateField(
        allow_null=True,
        required=False,
        help_text='Echo of the applied `start_date` filter, or null when omitted.',
    )
    end_date = serializers.DateField(
        allow_null=True,
        required=False,
        help_text='Echo of the applied `end_date` filter, or null when omitted.',
    )
    count = serializers.IntegerField(help_text='Total number of results across all pages.')
    next = serializers.URLField(
        allow_null=True,
        required=False,
        help_text='URL for the next page, or null on the last page.',
    )
    previous = serializers.URLField(
        allow_null=True,
        required=False,
        help_text='URL for the previous page, or null on the first page.',
    )
    results = serializers.ListField(
        child=serializers.DictField(),
        help_text='Page of result objects. Shape depends on the endpoint.',
    )


class SalesByDayQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(
        required=True,
        help_text='Inclusive start date (ISO 8601). Required.',
    )
    end_date = serializers.DateField(
        required=True,
        help_text='Inclusive end date (ISO 8601). Required; max 365 days after `start_date`.',
    )

    def validate(self, attrs):
        start = attrs['start_date']
        end = attrs['end_date']
        if start > end:
            raise serializers.ValidationError('start_date cannot be greater than end_date')
        if (end - start).days > 365:
            raise serializers.ValidationError('Date range cannot exceed 365 days')
        return attrs