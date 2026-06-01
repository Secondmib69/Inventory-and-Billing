from django.urls import path
from .views import *

app_name = 'invoices'

urlpatterns = [
    path('list/', InvoiceListAPIView.as_view(), name='invoice_list'),
    path('<int:id>/', InvoiceDetailAPIView.as_view(), name='invoice_detail'),
    path('<id>/pdf/', InvoicePDFDwonloadView.as_view(), name='invoice_pdf'),
]