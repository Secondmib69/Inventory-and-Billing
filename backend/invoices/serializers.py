
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
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
        help_text='Product primary key (write-only; use on create).',
    )

    class Meta:
        model = InvoiceItem
        fields = ['product', 'product_id', 'quantity', 'unit_price', 'item_total_price']
        read_only_fields = ['unit_price', 'item_total_price']
        extra_kwargs = {
            'quantity': {'help_text': 'Number of units to sell (must not exceed available stock).'},
            'unit_price': {'help_text': 'Price per unit, copied from the product at creation time.'},
            'item_total_price': {'help_text': 'Line total (`quantity` × `unit_price`), set automatically.'},
        }



class InvoiceSerializer(serializers.ModelSerializer):

    items = InvoiceItemSerializer(many=True)

    class Meta:
        model = Invoice
        fields = ['id', 'invoice_number', 'customer_name', 'items', 'created_at', 'total_amount']
        read_only_fields = ['invoice_number', 'created_at', 'total_amount']
        extra_kwargs = {
            'customer_name': {'help_text': 'Name printed on the invoice.'},
            'invoice_number': {'help_text': 'Unique invoice identifier (auto-generated).'},
            'total_amount': {'help_text': 'Sum of all line-item totals (auto-calculated).'},
            'created_at': {'help_text': 'Timestamp when the invoice was created.'},
            'items': {'help_text': 'Line items. At least one item is required on create.'},
        }


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

