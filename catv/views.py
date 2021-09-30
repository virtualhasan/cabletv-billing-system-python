from django.db import transaction
from django.db.models.expressions import OuterRef, Subquery
from catv.forms import CustomerForm
from accounts.models import AuditTable
from datetime import datetime, timedelta
import json
import requests
from django.conf import settings
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from django.utils import timezone
from catv.models import Area, Bill, Company, Customer, Payment
from django.http.response import Http404, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum
from api.serializers import CustomerSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model

User = get_user_model()




#this is for index page or Dashboard
@login_required
def index(request):
    # area_import()
    # user_import()

    
    
    last_ten_payments = Payment.objects.all().order_by("-createAt")[:10]
    today = timezone.now()

    #GEt Collector list for index page
    collector_list = Payment.objects.filter(
         createAt__date=today) \
        .values('paidBy__first_name', 'paidBy__last_name') \
        .annotate(paidAmount=Sum('paidAmount')) \
        .annotate(discount=Sum('discount')
    )

    # if user is collection paymentlist will be this
    if request.user.is_collector:
        collector_list = Payment.objects.filter(
            paidBy=request.user,
            createAt__date=today) \
            .values('paidBy__first_name', 'paidBy__last_name') \
            .annotate(paidAmount=Sum('paidAmount')) \
            .annotate(discount=Sum('discount')
        )

    # Area wise Collection    
    area_wise_collect = Payment.objects.filter(
        createAt__date=today) \
        .values('customer__area__name')\
        .annotate(paidAmount=Sum('paidAmount')
    )
    area_wise_collect_total = area_wise_collect.aggregate(Sum('paidAmount')).get('paidAmount__sum')
    
    area_wise_customer_stats = Area.objects.values('name') \
        .annotate(total=Count('customers')) \
        .annotate(active=Count('customers', filter=Q(customers__isActive=True))) \
        .annotate(inactive=Count('customers', filter=Q(customers__isActive=False))) \
 

    last_dues_query= Payment.objects.filter(customer__area=OuterRef('id')).order_by('-id').values('dues')[:1]
    area_wise_dues = Area.objects.values('name').annotate(
        unpaid_bill_dues= Sum('customers__bills__monthlyCharge', filter=Q(customers__bills__isPaid=False)),
        last_payment_dues = Subquery(last_dues_query)
    )

    area_wise_customer_stats_list = list(area_wise_customer_stats)
    grand_total = 0
    for area in area_wise_dues:
        last_payment_dues = 0 if area['last_payment_dues'] == None else area['last_payment_dues'] 
        unpaid_bill_dues = 0 if area['unpaid_bill_dues'] == None else area['unpaid_bill_dues'] 
        total_dues = last_payment_dues + unpaid_bill_dues
        grand_total += total_dues

        for key,value in enumerate(area_wise_customer_stats_list):
            if value['name'] == area['name']:
                area_wise_customer_stats_list[key]['total_dues'] = total_dues


    area_stats_total = {
        'total': area_wise_customer_stats.aggregate(Sum('total'))['total__sum'],
        'grand_total': grand_total,
        'active': area_wise_customer_stats.aggregate(Sum('active'))['active__sum'],
        'inactive': area_wise_customer_stats.aggregate(Sum('inactive'))['inactive__sum'],
    }


    comapany_details = Company.objects.last()
    context = {
        'company':comapany_details,
        'payment_list':last_ten_payments,
        'collector_list':collector_list,
        'area_wise_collect':area_wise_collect,
        'area_wise_collect_total':area_wise_collect_total,
        'area_stats':area_wise_customer_stats_list,
        'area_stats_total':area_stats_total,  
    }
    return render(request, 'index.html', context)


#Page Customer funtionlity
@login_required
# @user_passes_test(lambda user: user.is_superuser or user.is_admin)
def customers(request):
    customers = Customer.objects.select_related('area').all()
    area_list = Area.objects.all()
    
    form = CustomerForm()

    comapany_details = Company.objects.last()
    context = {
        "customers_list": customers,
        'area_list':area_list,
        'form':form,
        'company':comapany_details,
    }
    return render(request, 'customers.html', context)


@login_required
# @user_passes_test(lambda user: user.is_superuser or user.is_admin)
def add_customers(request):
    area = Area.objects.all()
    customers = Customer.objects.all().order_by('-createAt')[:10]
    comapany_details = Company.objects.last()
    return render(request, 'add-customers.html', {'area_list':area, 'customers_list':customers,'compayny':comapany_details})


@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def customer_inactive(request, id):
    customer = get_object_or_404(Customer, id=id)
    is_active =json.loads(request.POST.get('isActive'))
    is_bill_delete_or_generate = json.loads(request.POST.get('isBillDeleteOrGenerate'))
    today = timezone.now().replace(day=1) - timedelta(days=1)
    old_value = customer.isActive

    if request.method == "POST":
        try:
            with transaction.atomic():
                customer.isActive = not is_active #if active customer then it will be inactive
                customer.updateBy = request.user
                customer.save()
                print(customer.isActive)

                if is_active: #if user want to customer inactive and last bill delete
                    if is_bill_delete_or_generate:
                        Bill.objects.filter(
                            customer=customer, 
                            month=today.strftime('%B'), 
                            year=today.year,
                            isPaid=False
                        ).delete()
                else:
                    if is_bill_delete_or_generate: # if user want to customer active and generate last month bill
                        Bill.objects.create(
                            month=today.strftime('%B'),
                            year=today.year,
                            customer=customer,
                            monthlyCharge= customer.monthlyCharge,
                            createBy= request.user
                        )

                AuditTable.objects.create(
                        table='Customer', 
                        field='isActive',
                        record_id= id, 
                        old_value= old_value, 
                        new_value= customer.isActive,
                        add_by= request.user
                        )

                return JsonResponse({'success':True})

        except:
            return JsonResponse({'success':False, 'message':'not update'})
    return JsonResponse(data={'message':'ok'},status=500)
       
    


@login_required
def customers_by_name_or_mobile(request):
    name = request.GET.get('value')

    if name:
        customers = Customer.objects.filter(Q(name__contains=name) | Q(mobileNumber__contains=name))
        serializer = CustomerSerializer(customers, many=True)
    else:
        return JsonResponse({'success':False, 'message':'provide name or mobile'})
    return JsonResponse(serializer.data, safe=False)


#this funtion for find out last customer id and next customer id
@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def get_next_id(request, area_id):
    area = get_object_or_404(Area, id=area_id)
    customer = area.customers.order_by('id').last()
    return JsonResponse({'lastId':customer.id,'nextId':customer.id +1 })


@login_required
def bills(request):
    comapany_details = Company.objects.last()
    return render(request, 'bills.html', {'company':comapany_details})



@login_required
def reports(request):
    area_list = Area.objects.all()
    user_list = User.objects.all()
    comapany_details = Company.objects.last()

    context = {
        'area_list':area_list,
        'user_list':user_list,
        'company':comapany_details,
    }
    return render(request, 'reports.html', context)


@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def single_report(request):
    id = request.GET.get('id', None)
    try:
        customer = Customer.objects.select_related('area').get(id=id)
        payments = customer.payments.all().order_by('-id')
    except Customer.DoesNotExist:
        raise Http404

    comapany_details = Company.objects.last()
    context = {
        'customer':customer,
        'payment_list': payments,
        'company': comapany_details,
    }
    return render(request, 'singlereport.html', context=context) 



@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def monthly_report(request):
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)

    qs_date = request.GET.get('date', None)
    if qs_date is not None:
        payments = Payment.objects.filter(createAt__date=qs_date)
        month_name = qs_date
    else:
        payments = Payment.objects.filter(createAt__month=month, createAt__year=year)
        month_str = datetime.strptime(month,"%m").strftime("%B")
        month_name =f"{month_str}-{year}" 
    total = payments.aggregate(Sum('paidAmount')).get('paidAmount__sum')


    company_details = Company.objects.last()
    context = {
        'payment_list':payments,
        'total': total,
        'month_name': month_name,
        
    }
    return render(request, 'monthly-report.html', context)



#Area Details all with bills
@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def area_report(request):
    area_id = request.GET.get('area', None)
    isActive = request.GET.get('isActive', None)
    area_name = Area.objects.get(id=area_id).name

    if isActive == '2':
        customers = Customer.objects.select_related('area').filter(area=area_id)
    else:
        customers = Customer.objects.select_related('area').filter(area=area_id, isActive=isActive)

    all = [[customer.get_total_dues(), customer.this_month_paid_amount() if customer.this_month_paid_amount() != '' else 0] for customer in customers]
    total_dues = sum([ one[0] for one in all])
    total_paid = sum([ one[1] for one in all])

    today = timezone.now()
    first = today.replace(day=1)
    pre_month = first - timedelta(days=1)
    month_name = pre_month.strftime("%B-%Y")

    company_details= Company.objects.last()
    context = {
        'area_name':area_name,
        'month_name':month_name,
        'customer_list':customers,
        'total_dues':total_dues,
        'total_paid':total_paid,
        'company': company_details,
    }
    return render(request, 'area-report.html', context)



#User wise monthly report
@login_required
def user_report_view(request):
    user_id = request.GET.get('user', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    date = request.GET.get('date', None)
    user = get_object_or_404(User, id=user_id)
    full_name = user.get_full_name()

    if date:
        payment_list = Payment.objects.filter(paidBy=user, createAt__date=date)
    else:
        payment_list = Payment.objects.filter(paidBy=user, createAt__month=month, createAt__year=year)

    if request.user.is_collector:   
        full_name = request.user.get_full_name()
        if date:
            payment_list = Payment.objects.filter(paidBy=request.user, createAt__date=date)
        else:
            payment_list = Payment.objects.filter(paidBy=request.user, createAt__month=month, createAt__year=year)

    
    total = payment_list.aggregate(Sum('paidAmount'))['paidAmount__sum']

    context = {
        'payment_list':payment_list,
        'username':full_name,
        'total':total,
    }

    return render(request, 'user-report.html', context)



#app Settings here
@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def settings_view(request):
    area_name = request.POST.get('area_name')
    area_list = Area.objects.all()

    if request.method == "POST":
        if area_name != '' and not area_name.isnumeric():
            Area.objects.create(name=area_name)
            return redirect('settings')
        else:
            return HttpResponse("please provide area name")

    comapany_details = Company.objects.last()
    context= {
        "area_list":area_list,
        "company":comapany_details,
    }
    return render(request, 'settings.html', context)


#Check sms balance from api
def sms_check_view(request):
    try:
        response = requests.get(f'https://api.greenweb.com.bd/g_api.php?token={settings.SMS_API_TOKEN}&balance&expiry&json&rate', timeout=10)
        sms_balance = response.json()[0]['response']
        sms_expiry_date = response.json()[1]['response']
        sms_rate = response.json()[2]['response']
    except requests.exceptions.RequestException:
        return JsonResponse({"message":"error"})

    context = {
        'balance':sms_balance,
        'expiry':sms_expiry_date,
        'rate':sms_rate,
    }
    return JsonResponse(context)



#Previous Dues Updater month wise
@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def previous_bill_updater(request, id):
    preDues = int(request.POST.get('preDues', 0)) # get total previous dues from user
    customer = get_object_or_404(Customer, id=id)
    monthly_charge = customer.monthlyCharge 


    fraction_dues = preDues % monthly_charge  # get fraction dues from total dues
    total_month = int(preDues // monthly_charge)
    today = timezone.now().replace(day=1) # point current month

    if preDues < monthly_charge : #this is for when predues is less then monthlycharge
        total_month = 1
        monthly_charge = 0

    with transaction.atomic():
        counter = 0
        while counter < total_month:
            today -= timedelta(days=1)
            month_name = today.strftime('%B')

            if not Bill.objects.filter(month=month_name, year=today.year, customer=customer):
                if counter == total_month-1:
                    monthly_charge += fraction_dues

                Bill.objects.create(
                    month=month_name,
                    year= today.year,
                    monthlyCharge=monthly_charge,
                    customer=customer
                    )
                counter += 1 # increase counter

        return JsonResponse({'success':True,'message':'updated'})
    return JsonResponse({'message':'error'})





from .utils import area_import, monthly_bill_generator, user_import
def generate_bills(request):
    if monthly_bill_generator():
        return JsonResponse({"success":True, "message":"bill generated"})