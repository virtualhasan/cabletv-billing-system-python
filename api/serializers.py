from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import fields
from catv.models import Area, Bill, Customer, Payment
from rest_framework import serializers


class AreaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Area
        fields = ['id', 'name']


class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    totalDues = serializers.DecimalField(source='get_total_dues', read_only=True, max_digits=7, decimal_places=2)

    class Meta:
        model = Customer
        exclude = ('createAt', 'updateAt', "createBy", 'updateBy')
        read_only_fields = ['isActive', 'geoLocation']

    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['area'] = AreaSerializer(instance.area).data
        return response

    def validate_id(self, value):
        try:
            customer = Customer.objects.get(id=value)
            raise ValidationError('customer already exist')
        except Customer.DoesNotExist:
            return value

class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        exclude = ('createAt', 'updateAt', "createBy", 'updateBy','isActive', 'geoLocation')

class BillSerializer(serializers.ModelSerializer):
    monthlyCharge = serializers.SerializerMethodField()
    
    class Meta:
        model = Bill
        fields = ('id', 'month', 'year', 'monthlyCharge', 'isPaid')

    def get_monthlyCharge(self, obj):
        return (obj.monthlyCharge - obj.permanentDiscount)


class PaymentSerializer(serializers.ModelSerializer):
    bills = BillSerializer(many=True, read_only=True)

    class Meta:
        model = Payment
        exclude = ('createAt', 'updateAt', 'updateBy')


class MakePaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Payment
        fields = ('paidAmount', 'discount', 'txnId')
