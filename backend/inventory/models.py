from django.db import IntegrityError, models
from django.utils.text import slugify
import string
import random

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=250)
    sku = models.CharField(max_length=50, unique=True)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'product: {self.name} with sku: {self.sku}'
    
    def _sku_generator(self):
        base = slugify(self.name)[:20].upper() or 'PRODUCT'
        suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f'{base}-{suffix}'
    
    def save(self, *args, **kwargs):
        if not self.sku:
            while True: # we use this loop to avoid if theres a tiny chance generated sku already exists
                self.sku = self._sku_generator()
                try:
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    continue # Retry with a new SKU
        else:
            super().save(*args, **kwargs)
                
    
class StockMovement(models.Model):

    class ReasonChoices(models.TextChoices):
        SALE = 'Sale', 'Sale'
        PURCHASE = 'Purchase', 'Purchase'
        OTHER = 'Other', 'Other'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=50, choices=ReasonChoices, default=ReasonChoices.OTHER)
