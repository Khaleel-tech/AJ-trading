from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Item, Bill, BillItem

admin.site.register(Item)
admin.site.register(Bill)
admin.site.register(BillItem)
