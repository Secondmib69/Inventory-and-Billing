from rest_framework import serializers
from .models import Product, StockMovement
from django.db import transaction
from django.db.models import F

class ProductSeralizer(serializers.ModelSerializer):

    initial_stock = serializers.IntegerField(required=False, default=0, min_value=0,
     write_only=True, label='Initial Stock', help_text='existing stock (optional)')

    class Meta:
        model = Product
        fields = ['name', 'price', 'stock', 'sku', 'created_at', 'updated_at', 'initial_stock']
        read_only_fields = ['sku', 'stock']


    def create(self, validated_data):
        initial_stock = validated_data.pop('initial_stock', 0)
        with transaction.atomic():
            product = Product.objects.create(**validated_data)
            if initial_stock:
                StockMovement.objects.create(
                    product=product,
                    quantity=initial_stock,
                    reason=StockMovement.ReasonChoices.PURCHASE
                )
                Product.objects.filter(id=product.id).update(stock=F('stock') + initial_stock)
                product.refresh_from_db(fields=['stock']) # refreshes fetched data from db so we can see the right stock amount in 201 response

            return product