from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Bill, Company, Customer, Area, Payment
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()

# Unregister you models here
admin.site.unregister(Group)

# Register your models here.
admin.site.register(User)
admin.site.register(Company)
admin.site.register(Area)
admin.site.register(Customer)
admin.site.register(Bill)
admin.site.register(Payment)
