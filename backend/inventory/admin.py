from django.contrib import admin
from inventory.models import Product, StockMovement
from invoices.models import Invoice, InvoiceItem
from django.contrib.admin import TabularInline
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model

# Register your models here.
User = get_user_model()

class StockMovementInline(TabularInline):
    model = StockMovement
    extra = 0
    readonly_fields = ['created_at', 'move_type', 'quantity']
    can_delete = False

class InvoiceItemInline(TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['invoice', 'product', 'quantity', 'unit_price', 'item_total_price']
    can_delete = False
    

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ['id', 'username', 'email', 'is_staff', 'is_active']
    list_editable = ['is_staff', 'is_active']
    list_display_links = ['username']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    search_help_text = 'Search by username, firstname, lastname, email'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sku', 'stock']
    list_display_links = ['name']
    search_fields = ['name', 'sku']
    search_help_text = 'Search by product name or SKU'
    readonly_fields = ['sku']
    inlines = [StockMovementInline]

@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'move_type', 'reason', 'created_at']
    list_display_links = ['product']
    list_filter = ['move_type', 'reason', 'created_at']
    search_fields = ['product__name', 'product__sku']
    search_help_text = 'Search by product name or SKU'
    readonly_fields = ['id', 'product', 'move_type', 'reason', 'created_at', 'quantity']

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'invoice_number', 'customer_name', 'created_at', 'total_amount']
    list_display_links = ['invoice_number']
    list_filter = ['created_at']
    ordering = ['-created_at']
    search_fields = ['invoice_number', 'customer_name']
    search_help_text = 'Search by invoice number or customer name'
    inlines = [InvoiceItemInline]



