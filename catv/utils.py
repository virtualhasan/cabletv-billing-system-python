from .models import Area, Customer
import json

def area_import():
    areas = [
        {'id':11, 'name':"মথুরাপুর"},
        {'id':12, 'name':"বিরাহিমপুর"},
        {'id':13, 'name':"তালপট্টি"},
        {'id':14, 'name':"গোঁয়ালগাও"},
        {'id':15, 'name':"নির্ভয়পুর"},       
        {'id':16, 'name':"বিষ্ণুপুর"},       
        {'id':18, 'name':"লামপুর" },       
        {'id':32, 'name':"হিম্মতপুর" },       
    ]

    for area in areas:
        Area.objects.create(id=area['id'], name=area['name'])


def user_import():
    with open('clients.json', 'r', encoding='utf8') as f:
        data_set = json.load(f)[2]['data']

    for data in data_set:
        customer = Customer(
            id= data['id'],
            name= data['Name'],
            fatherName=data['Father'],
            address=data['Address'],
            area=Area.objects.get(id=data['AreaId']),
            mobileNumber=data['Mobile'],
            nidNumber=data['Nid'],
            occupation=data['Occupation'],
            isActive=data['Active'],
            connectionFee=data['ConnectionFee'],
            connectionAt=data['ConnectionDate'],
            tv=1,
            monthlyCharge=data['MonthlyCharge']
        )

        customer.save()
        print('user creating')

        





from django.utils import timezone
from .models import Bill, Customer
def monthly_bill_generator():
    today = timezone.now()
    year = today.year
    month = today.strftime("%B")
    print(year)
    print(month)

    customers = Customer.objects.filter(isActive=True)
    
    for customer in customers:
        print(customer)
        bill = Bill.objects.filter(customer=customer, month=month, year=year)
        if bill.exists():
            print(f'Aready Generated for this {customer.name}')
        else:
            Bill.objects.create(
                customer=customer,
                month=month,
                year=year,
                monthlyCharge=customer.monthlyCharge,
                permanentDiscount=customer.permanentDiscount  
            )
    return True




