from django_filters.rest_framework import filterset, DateFromToRangeFilter
from invoices.models import Invoice
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomDateFilter(filterset.FilterSet):

    created_at = DateFromToRangeFilter(field_name='created_at', lookup_expr='date')

    class Meta:
        model = Invoice
        fields = []


class ReportsPagination(PageNumberPagination):
    page_size = 20
    page_query_param = 'page'
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):

        return Response({
            "start_date": self.start_date,
            "end_date": self.end_date,
            "count": self.page.paginator.count,
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })