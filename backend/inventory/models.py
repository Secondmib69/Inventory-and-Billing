from django.db import IntegrityError, models, transaction
from django.utils.text import slugify
import string
import random

# Create your models here.

class Product(models.Model):
    name = models.CharField(max_length=250)
    sku = models.CharField(max_length=50, unique=True)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
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
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except IntegrityError:
                    continue # Retry with a new SKU
        else:
            return super().save(*args, **kwargs)
                
    
class StockMovement(models.Model):

    class ReasonChoices(models.TextChoices):
        SALE = 'Sale', 'Sale'
        PURCHASE = 'Purchase', 'Purchase'
        OTHER = 'Other', 'Other'

    class TypeChoices(models.TextChoices):
        MOVE_IN = 'IN', 'in'
        MOVE_OUT = 'OUT', 'out'

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_movements')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    quantity = models.PositiveIntegerField()
    reason = models.CharField(max_length=50, choices=ReasonChoices.choices, default=ReasonChoices.OTHER)
    move_type = models.CharField(max_length=5, choices=TypeChoices.choices, default=TypeChoices.MOVE_IN)

    def __str__(self):
        return f'{self.move_type} >> {self.product.name} ({self.quantity})'
    
    class Meta:
        indexes = [
            models.Index(fields=['product', 'move_type', 'created_at'])
        ]