from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.
class User(AbstractUser):
    is_collector = models.BooleanField('collector',default=False, help_text='if user is bill collector')
    is_admin = models.BooleanField('admin',default=False, help_text='if user is admin action')

    class Meta:
        verbose_name_plural = 'User'

class AuditTable(models.Model):
    table = models.CharField(max_length=200)
    field = models.CharField(max_length=200)
    record_id = models.IntegerField()
    old_value = models.TextField()
    new_value = models.TextField()
    add_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING)
    create_at = models.DateField(auto_now_add=True)


    class Meta:
        verbose_name_plural = 'History Table'

    def __str__(self):
        return f"{self.table} - {self.field}- by {self.add_by.username}"