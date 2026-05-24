from django.db import models

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=250)
    sku = models.CharField(max_length=50, unique=True)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
class StockMovement(models.Model):

    class ReasonChoices(models.TextChoices):
        SALE = 'Sale', 'Sale'
        PURCHASE = 'Purchase', 'Purchase'
        OTHER = 'Other', 'Other'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=50, choices=ReasonChoices, default=ReasonChoices.OTHER)
