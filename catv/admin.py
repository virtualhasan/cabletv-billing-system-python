from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Bill, Company, Customer, Area, Payment



# Unregister you models here
# Register your models here.
admin.site.register(Company)
admin.site.register(Area)
admin.site.register(Customer)
admin.site.register(Bill)
admin.site.register(Payment)
