from django.db import IntegrityError, models, transaction
from django.utils import timezone
from inventory.models import Product
import uuid

# Create your models here.


class Invoice(models.Model):
    invoice_number = models.CharField(unique=True, max_length=20, editable=False)
    customer_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    total_amount = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f'{self.invoice_number}>>{self.customer_name}'
    
    def _generate_invoice_number(self):
        year = timezone.now().year
        short_uuid = uuid.uuid4().hex[:10].upper() # generate a short uuid for our invoice
        return f'INV-{year}-{short_uuid}'
    
    def save(self, *args, **kwargs):
        if not self.invoice_number:
            while True:
                self.invoice_number = self._generate_invoice_number()
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except IntegrityError:
                    continue
        else:
            return super().save(*args, **kwargs)
    

class InvoiceItem(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=0)
    unit_price = models.PositiveBigIntegerField(default=0)
    item_total_price = models.PositiveBigIntegerField(default=0, editable=False)

    def save(self, *args, **kwargs):
        self.item_total_price = self.quantity * self.unit_price
        super().save(*args, **kwargs)

