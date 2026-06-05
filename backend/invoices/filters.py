from django_filters import RangeFilter, FilterSet
from rest_framework.exceptions import ValidationError
from .models import Invoice
from rest_framework.pagination import CursorPagination


class InvoiceFilter(FilterSet):

    total_amount = RangeFilter(
        field_name='total_amount',
        label='Total Amount Range',
        help_text='Filter invoices by total amount using `total_amount_min` and `total_amount_max`.',
    )

    @property
    def qs(self):
        parent = super().qs

        if not self.form.is_valid():
            return parent
        
        r = self.form.cleaned_data.get('total_amount')
        if not r:
            return parent
        
        min_val = getattr(r, 'start', None)
        max_val = getattr(r, 'stop', None)

        if min_val is not None and min_val < 0:
            raise ValidationError({"total_amount_min": "Cannot be negative."})
        if max_val is not None and max_val < 0:
            raise ValidationError({"total_amount_max": "Cannot be negative."})
        
        if min_val is not None and max_val is not None and min_val > max_val:
            raise ValidationError({"total_amount": "Minimum total cannot be greater than maximum total."})
        return parent
        


    class Meta:
        model = Invoice
        fields = []


class InvoicePagination(CursorPagination):
    page_size = 20
    ordering = '-created_at'