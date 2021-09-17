from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    is_collector = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

class AuditTable(models.Model):
    table = models.CharField(max_length=200)
    field = models.CharField(max_length=200)
    record_id = models.IntegerField()
    old_value = models.TextField()
    new_value = models.TextField()
    add_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    create_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.table} - {self.field}- by {self.add_by.username}"