from rest_framework import serializers
from inventory.models import Product
from invoices.serializers import ProductMiniSerializer
class SalesSummarySerializer(serializers.Serializer):

    average_invoice = serializers.IntegerField()
    invoice_count = serializers.IntegerField()
    total_revenue = serializers.BigIntegerField()


class TopSellingSerializer(serializers.ModelSerializer):

    stock_sold = serializers.IntegerField()
    revenue = serializers.IntegerField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'sku','stock_sold', 'revenue']