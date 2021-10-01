from django.db import models
from django.db.models.aggregates import Sum 
from django.utils import timezone
from django.conf import settings



class Company(models.Model):
    name = models.CharField(max_length=250)
    banglaName = models.CharField(max_length=250)
    shortName = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=250)
    mobileNumber = models.CharField(max_length=11)
    alterMobileNunmber = models.CharField(max_length=11, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'Company'

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField(max_length=50, unique=True)
    class Meta:
        verbose_name_plural = "Area"

    def __str__(self):
        return f'{self.id} - {self.name}'



class Customer(models.Model):
    name = models.CharField(max_length=100)
    fatherName = models.CharField(max_length=100, blank=True)
    address = models.CharField(max_length=200, blank=True)
    area = models.ForeignKey(Area, on_delete=models.DO_NOTHING, related_name='customers')
    mobileNumber = models.CharField(max_length=11, blank=True)
    nidNumber = models.CharField(max_length=20, blank=True)
    occupation = models.CharField(max_length=30, blank=True)
    geoLocation = models.JSONField(blank=True, null=True)
    isActive = models.BooleanField(default=True)
    connectionFee = models.DecimalField(max_digits=7, decimal_places=2, default=1000)
    connectionAt = models.DateField(blank=True, null=True)
    tv = models.PositiveIntegerField(default=1)
    monthlyCharge = models.DecimalField(max_digits=6, decimal_places=2, default=200)

    createBy = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.DO_NOTHING, related_name='created_user')
    updateBy = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.DO_NOTHING, related_name='updated_user')
    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.id} - {self.name} - {self.area.name}'

    def get_total_dues(self):
        dues = self.bills.filter(isPaid=False).aggregate(total =Sum('monthlyCharge'))['total']
        dues = dues if dues else 0 
        last_payment = self.payments.last()
        dues += last_payment.dues if last_payment else 0
        return dues
        

    def this_month_paid_amount(self):
        today = timezone.now()
        payment = self.payments.filter(
            createAt__month=today.month,
            createAt__year= today.year
        ).aggregate(Sum('paidAmount'))['paidAmount__sum']
        return payment if payment else ''



class Bill(models.Model):
    month = models.CharField(max_length=20)
    year = models.CharField(max_length=4)
    monthlyCharge = models.DecimalField(max_digits=6, decimal_places=2)
    isPaid = models.BooleanField(default=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bills')
    payment = models.ForeignKey('Payment', null=True, blank=True, on_delete=models.CASCADE, related_name='bills')
    createBy = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.DO_NOTHING, related_name='created_bill')
    updateBy = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.DO_NOTHING, related_name='updated_bill')
    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('month', 'year','customer',)

    def __str__(self):
        return f'{self.customer.id}-{self.customer.name}-{self.month}-{self.year}'



class Payment(models.Model):
    CASH = 'cash'
    BKASH = 'bkash'
    ROCKET = 'rocket'
    NAGAD = 'nagad'
    UPAY = 'upay'

    PAYMENT_METHOD = (
        (CASH, 'Cash'),
        (BKASH, 'Bkash'),
        (NAGAD, 'Nagad'),
        (ROCKET, 'Rocket'),
        (UPAY, 'Upay')
    )

    totalAmount = models.DecimalField(max_digits=7, decimal_places=2)
    paidAmount = models.DecimalField(max_digits=7, decimal_places=2)
    discount = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    #total previous dues include this last payment
    dues = models.DecimalField(max_digits=7, decimal_places=2, default=0)
    paymentMethod = models.CharField(max_length=20,choices=PAYMENT_METHOD, default=CASH)
    accountNumber = models.CharField(max_length=11, blank=True, default='')
    txnId = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE, related_name='payments')
    paidBy = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, on_delete=models.DO_NOTHING, related_name='payments')
    updateBy = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.DO_NOTHING, related_name='update_payments')
    createAt = models.DateTimeField(auto_now_add=True)
    updateAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.customer.id}-{self.customer.name}-{self.paidAmount}'

    def get_this_payment_dues(self):
        return self.totalAmount - (self.paidAmount + self.discount)

    def get_bill_month_name(self):
        return ''.join([f'{bill.month[:3]}-{bill.year}' for bill in self.bills.all()])