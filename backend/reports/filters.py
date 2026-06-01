from django_filters.rest_framework import filterset, DateFromToRangeFilter
from invoices.models import Invoice

class CustomDateFilter(filterset.FilterSet):

    created_at = DateFromToRangeFilter(field_name='created_at', lookup_expr='date')

    class Meta:
        model = Invoice
        fields = []
