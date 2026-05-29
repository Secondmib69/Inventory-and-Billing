
from rest_framework import serializers, reverse
from .models import Invoice, InvoiceItem
from inventory.models import Product, StockMovement
from django.db import transaction
from django.db.models import F


class ProductMiniSerializer(serializers.ModelSerializer):

    details = serializers.HyperlinkedIdentityField(view_name='inventory:product_detail', lookup_field='id')

    class Meta:
        model = Product
        fields = ['id', 'name', 'details']


class InvoiceItemSerializer(serializers.ModelSerializer):

    # def get_product(self, obj):
    #     request = self.context.get('request')
    #     url = reverse.reverse('inventory:product_detail', request=request, kwargs={'id': obj.product.id})
    #     return {
    #         'id': obj.product.id,
    #         'name': obj.product.name,
    #         'details': url
    #     }


    # product = serializers.SerializerMethodField()
    product = ProductMiniSerializer(read_only=True)
    

    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'unit_price', 'item_total_price']
        read_only_fields = ['unit_price', 'item_total_price']



class InvoiceSerializer(serializers.ModelSerializer):

    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'customer_name', 'items', 'created_at', 'total_amount']
        read_only_fields = ['invoice_number', 'created_at', 'total_amount']


    def create(self, validated_data):
        with transaction.atomic():
            items = validated_data.pop('items')
            invoice = Invoice.objects.create(**validated_data)
            total_amount = 0
            for item in items:
                product = Product.objects.select_for_update().get(pk=item['product'].pk)
                quantity = item['quantity']
                unit_price = product.price

                if product.stock < quantity:
                    raise serializers.ValidationError(f'insufficient stock for {product.name}!, available: {product.stock}')
                
                invoice_item = InvoiceItem(product=product, quantity=quantity, unit_price=unit_price, invoice=invoice)
                invoice_item.save() # item_total_price will be generated
                total_amount += invoice_item.item_total_price
                product.stock = F('stock') - quantity
                product.save(update_fields=['stock'])

                StockMovement.objects.create(product=product, quantity=quantity, 
                    reason=StockMovement.ReasonChoices.SALE, move_type=StockMovement.TypeChoices.MOVE_OUT)
            invoice.total_amount = total_amount
            invoice.save(update_fields=['total_amount'])
            return invoice

