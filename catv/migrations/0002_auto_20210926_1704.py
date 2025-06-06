# Generated by Django 3.2.4 on 2021-09-26 17:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('catv', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='company',
            name='mobileNumber2',
        ),
        migrations.AddField(
            model_name='company',
            name='alterMobileNunmber',
            field=models.CharField(blank=True, max_length=11, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='bangla_name',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='company',
            name='shortName',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='bill',
            name='payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='bills', to='catv.payment'),
        ),
    ]
