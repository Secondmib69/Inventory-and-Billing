from rest_framework import serializers
from inventory.models import Product
from invoices.serializers import ProductMiniSerializer
from rest_framework.reverse import reverse


class SalesSummarySerializer(serializers.Serializer):


    average_invoice = serializers.IntegerField()
    invoice_count = serializers.IntegerField()
    total_revenue = serializers.BigIntegerField()


class SalesSummaryQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)


class TopSellingSerializer(serializers.ModelSerializer):

    def get_details(self, obj):
        request = self.context.get('request')
        url = reverse(request=request, viewname='inventory:product_detail', kwargs={'id': obj.id})
        return url
    

    details = serializers.SerializerMethodField()
    stock_sold = serializers.IntegerField()
    revenue = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'details','stock_sold', 'revenue']


class SalesByDaySerializer(serializers.Serializer):

    day = serializers.DateField()
    revenue = serializers.BigIntegerField()

class SalesByDayQuerySerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

    def validate(self, attrs):
        start = attrs['start_date']
        end = attrs['end_date']
        if start > end:
            raise serializers.ValidationError('start_date cannot be greater than end_date')
        if (end - start).days > 365:
            raise serializers.ValidationError('Date range cannot exceed 365 days')
        return attrs