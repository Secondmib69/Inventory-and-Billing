from rest_framework import serializers
from .models import Product, StockMovement
from django.db import transaction
from django.db.models import F

class ProductSeralizer(serializers.ModelSerializer):

    initial_stock = serializers.IntegerField(required=False, default=0, min_value=0,
     write_only=True, label='Initial Stock', help_text='existing stock (optional)')

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'stock', 'sku', 'created_at', 'updated_at', 'initial_stock']
        read_only_fields = ['sku', 'stock']


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


