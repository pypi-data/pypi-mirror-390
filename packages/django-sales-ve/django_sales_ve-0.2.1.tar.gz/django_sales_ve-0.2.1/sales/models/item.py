from django.db import models
from sales.enums import ItemType


class UoM(models.Model):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=64)
    def __str__(self):
        return self.code


class Item(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    sku = models.CharField(max_length=64)
    name = models.CharField(max_length=200)
    type = models.CharField(max_length=16, choices=[(t.value, t.value) for t in ItemType])
    uom = models.ForeignKey(UoM, on_delete=models.PROTECT, null=True, blank=True)
    sales_price = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    tax = models.ForeignKey("finacc.Tax", on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    class Meta:
        unique_together = ("company", "sku")
    def __str__(self):
         return f"{self.sku} — {self.name}"


class PriceList(models.Model):
    company = models.ForeignKey("finacc.Company", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    currency = models.CharField(max_length=3, default="INR")
    is_default = models.BooleanField(default=False)


class Price(models.Model):
    price_list = models.ForeignKey(PriceList, on_delete=models.CASCADE, related_name="prices")
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    rate = models.DecimalField(max_digits=18, decimal_places=2)
    class Meta:
        unique_together = ("price_list", "item")