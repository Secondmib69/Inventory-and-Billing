from django_filters import FilterSet, NumberFilter
from rest_framework import exceptions, pagination
from .models import Product






class ProductFilter(FilterSet):

    min_price = NumberFilter(
        field_name='price',
        lookup_expr='gte',
        label='Minimum Price',
        help_text='Products with price greater than or equal to this value (≥ 0).',
    )
    max_price = NumberFilter(
        field_name='price',
        lookup_expr='lte',
        label='Maximum Price',
        help_text='Products with price less than or equal to this value (≥ 0).',
    )
    min_stock = NumberFilter(
        field_name='stock',
        lookup_expr='gte',
        label='Minimum Stock',
        help_text='Products with stock greater than or equal to this value (≥ 0).',
    )
    max_stock = NumberFilter(
        field_name='stock',
        lookup_expr='lte',
        label='Maximum Stock',
        help_text='Products with stock less than or equal to this value (≥ 0).',
    )
    # stock = RangeFilter(field_name='stock', label='Stock Range')

    class Meta:
        model = Product
        fields = []

    @property
    def qs(self):
        parent = super().qs
    
        if not self.form.is_valid():
            return parent

        min_price = self.form.cleaned_data.get('min_price')
        max_price = self.form.cleaned_data.get('max_price')
        min_stock = self.form.cleaned_data.get('min_stock')
        max_stock = self.form.cleaned_data.get('max_stock')

        # Check for negative values
        if any(v is not None and v < 0 for v in [min_price, max_price, min_stock, max_stock]):
            raise exceptions.ValidationError('Values cannot be negative.')

        # Check Price Range
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise exceptions.ValidationError({'price_range': 'Minimum price cannot be greater than maximum price.'})

        # Check Stock Range
        if min_stock is not None and max_stock is not None:
            if min_stock > max_stock:
                raise exceptions.ValidationError({'stock_range': 'Minimum stock cannot be greater than maximum stock.'})

        return parent
    

class ProductPagePagination(pagination.PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100


class StockMovementPagination(pagination.CursorPagination):
    page_size = 20
    ordering = '-created_at'
