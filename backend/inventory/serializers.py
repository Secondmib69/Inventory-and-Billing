from rest_framework import serializers
from .models import Product, StockMovement
from django.db import transaction
from django.db.models import F

class ProductSeralizer(serializers.ModelSerializer):

    initial_stock = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
        write_only=True,
        label='Initial Stock',
        help_text='Optional seed quantity. Creates an IN stock movement on product creation.',
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'sku', 'created_at', 'updated_at', 'initial_stock']
        read_only_fields = ['sku', 'stock']
        extra_kwargs = {
            'name': {'help_text': 'Display name of the product.'},
            'price': {'help_text': 'Unit price as a positive integer.'},
            'stock': {'help_text': 'Current on-hand quantity (read-only; changed via stock movements).'},
            'sku': {'help_text': 'Auto-generated stock-keeping unit (read-only).'},
            'created_at': {'help_text': 'Timestamp when the product was created.'},
            'updated_at': {'help_text': 'Timestamp of the last product update.'},
        }


    def create(self, validated_data):
        initial_stock = validated_data.pop('initial_stock', 0)
        with transaction.atomic():
            product = Product.objects.create(**validated_data)
            if initial_stock and initial_stock > 0:
                StockMovement.objects.create(
                    product=product,
                    quantity=initial_stock,
                    reason=StockMovement.ReasonChoices.PURCHASE,
                    move_type=StockMovement.TypeChoices.MOVE_IN
                )
                product.stock = F('stock') + initial_stock
                product.save(update_fields=['stock'])# we can use Product.objects.filter.update but that wont track signals
                product.refresh_from_db(fields=['stock']) # refreshes fetched data from db so we can see the right stock amount in 201 response

            return product
        

class StockMovementSerializer(serializers.ModelSerializer):

    class Meta:
        model = StockMovement
        fields = ['id', 'product', 'quantity', 'move_type', 'created_at', 'reason']
        extra_kwargs = {
            'product': {'help_text': 'Product primary key.'},
            'quantity': {'help_text': 'Units moved (positive integer).'},
            'move_type': {
                'help_text': 'Direction of movement: `IN` adds stock, `OUT` subtracts stock.',
            },
            'reason': {
                'help_text': 'Why the movement occurred: `Sale`, `Purchase`, or `Other`.',
            },
            'created_at': {'help_text': 'Timestamp when the movement was recorded.'},
        }

    def validate(self, attrs):
        product = attrs['product']
        quantity = attrs['quantity']
        move_type = attrs['move_type']

        if move_type == StockMovement.TypeChoices.MOVE_OUT and product.stock < quantity:
            raise serializers.ValidationError(f'insufficient stock! available: {product.stock}')
        return attrs
    
    def create(self, validated_data):

        with transaction.atomic():
            # to prevent other requests from changing stock while we calculate.
            # select_for_update() locks this row until the 'with' block ends
            product = Product.objects.select_for_update().get(pk=validated_data['product'].pk) 
            quantity = validated_data['quantity']
            move_type = validated_data['move_type']

            # Now that we have the lock, we check the REAL stock for the last time
            if move_type == StockMovement.TypeChoices.MOVE_OUT and product.stock < quantity:
                raise serializers.ValidationError(f'insufficient stock! available: {product.stock}')
            stm = StockMovement.objects.create(**validated_data)
            if move_type == StockMovement.TypeChoices.MOVE_OUT:
                product.stock = F('stock') - quantity
            if move_type == StockMovement.TypeChoices.MOVE_IN:
                product.stock = F('stock') + quantity
            product.save(update_fields=['stock'])
            return stm


