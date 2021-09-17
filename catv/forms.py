from catv.models import Customer
from django import forms


class CustomerForm(forms.ModelForm):
    id = forms.IntegerField()

    class Meta:
        model = Customer
        exclude = ('geoLocation','isActive', 'createBy', 'updateBy', 'createAt','updateAt')