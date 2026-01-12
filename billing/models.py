from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


from django.db import models

class Bill(models.Model):
    invoice_number = models.CharField(max_length=20, unique=True)

    customer_name = models.CharField(max_length=100)
    customer_mobile = models.CharField(max_length=15)
    customer_address = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    # Extra charges
    labour_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vehicle_rent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    railway_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tray_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    advance_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    pdf = models.FileField(upload_to="bills/", blank=True, null=True)

    # 🔴 NEW FIELDS (for Removed Bills feature)
    is_removed = models.BooleanField(default=False)
    removed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.invoice_number

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    suit = models.IntegerField(default=0)
    net_weight = models.DecimalField(decimal_places=2, max_digits=10)
    price = models.DecimalField(max_digits=10, decimal_places=1)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.name} ({self.quantity})"


class RemovedItem(models.Model):
    item_name = models.CharField(max_length=100, blank=True, null=True,default=None)
    removed_price = models.DecimalField(max_digits=10, decimal_places=2)
    removed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.item_name} - {self.removed_price}"


