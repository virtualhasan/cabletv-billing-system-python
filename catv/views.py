from catv.forms import CustomerForm
from accounts.models import AuditTable
from datetime import datetime, timedelta
import json
import requests
from django.conf import settings
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q
from django.utils import timezone
from catv.models import Area, Bill, Customer, Payment
from django.http.response import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Sum
from api.serializers import CustomerSerializer
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model

User = get_user_model()

#this is for index page or Dashboard
@login_required
def index(request):

    # user_import()


    last_ten_payments = Payment.objects.all().order_by("-createAt")[:10]
    today = timezone.now()
    collector_list = Payment.objects.filter(createAt__date=today).values('paidBy__first_name', 'paidBy__last_name').annotate(paidAmount=Sum('paidAmount')).annotate(discount=Sum('discount'))

    if request.user.is_collector:
        collector_list = Payment.objects.filter(paidBy=request.user,createAt__date=today).values('paidBy__first_name', 'paidBy__last_name').annotate(paidAmount=Sum('paidAmount')).annotate(discount=Sum('discount'))

    # Area wise Collection    
    area_wise_collect = Payment.objects.filter(createAt__date=today).values('customer__area__name').annotate(paidAmount=Sum('paidAmount'))
    area_wise_collect_total = area_wise_collect.aggregate(Sum('paidAmount')).get('paidAmount__sum')


    area_info = Area.objects.all()
    area_details = []
    for area in area_info:
        all_customer = area.customers.all()
        total_dues = 0
        active = 0
        in_active = 0
        for customer in all_customer:
            total_dues += customer.get_total_dues()
            if customer.isActive:
                active += 1
            else:
                in_active += 1
        area_details.append({
            'name':area.name,
            'dues': total_dues,
            "total":all_customer.count(),
            'active':active, 
            'inActive':in_active
        })

    
    grand_total = 0
    grand_active = 0
    grand_inActive = 0
    grand_total_dues = 0
    for area_total in area_details:
        grand_total += area_total['total']
        grand_active += area_total['active']
        grand_inActive += area_total['inActive']
        grand_total_dues += area_total['dues']
    total_array = [grand_total, grand_active, grand_inActive, grand_total_dues]


    context = {
        'payment_list':last_ten_payments,
        'collector_list':collector_list,
        'area_wise_collect':area_wise_collect,
        'area_wise_collect_total':area_wise_collect_total,
        'area_details':area_details,
        'total_details':total_array,      
    }
    return render(request, 'index.html', context)


#Page Customer funtionlity
@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def customers(request):
    customers = Customer.objects.all()
    area_list = Area.objects.all()
    
    form = CustomerForm()

    context = {
        "customers_list": customers,
        'area_list':area_list,
        'form':form,
    }
    return render(request, 'customers.html', context)


@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def add_customers(request):
    area = Area.objects.all()
    customers = Customer.objects.all().order_by('-createAt')[:10]
    return render(request, 'add-customers.html', {'area_list':area, 'customers_list':customers})


@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def customer_inactive(request, id):
    customer = get_object_or_404(Customer, id=id)
    isActive = json.loads(request.POST.get('isActive'))

    if request.method == "POST":
        try:
            AuditTable.objects.create(
                table='Customer', 
                field='isActive',
                record_id=id, 
                old_value=customer.isActive, 
                new_value=isActive,
                add_by= request.user
                )


            customer.isActive = isActive
            customer.updateBy = request.user
            customer.save()
            
            return JsonResponse({'success':True})
        except:
            return JsonResponse({'success':False, 'message':'not update'})
    return JsonResponse(status=500)


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
    return render(request, 'bills.html', {})



@login_required
def reports(request):
    area_list = Area.objects.all()
    user_list = User.objects.all()

    context = {
        'area_list':area_list,
        'user_list':user_list,
    }
    return render(request, 'reports.html', context)


@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def single_report(request):
    id = request.GET.get('id', None)
    try:
        customer = Customer.objects.get(id=id)
    except Customer.DoesNotExist:
        raise Http404

    context = {
        'customer':customer,
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
        customers = Customer.objects.filter(area=area_id)
    else:
        customers = Customer.objects.filter(area=area_id, isActive=isActive)


    today = timezone.now()
    first = today.replace(day=1)
    pre_month = first - timedelta(days=1)
    month_name = pre_month.strftime("%B-%Y")

    context = {
        'area_name':area_name,
        'month_name':month_name,
        'customer_list':customers,
    }
    return render(request, 'area-report.html', context)



#User wise monthly report
@login_required
def user_report_view(request):
    user_id = request.GET.get('user', None)
    month = request.GET.get('month', None)
    year = request.GET.get('year', None)
    user = get_object_or_404(User, id=user_id)
    full_name = user.get_full_name()

    payment_list = Payment.objects.filter(paidBy=user, createAt__month=month, createAt__year=year)


    if request.user.is_collector:   
        full_name = request.user.get_full_name()
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

    context= {
        "area_list":area_list
    }
    return render(request, 'settings.html', context)


#Check sms balance from api
def sms_check_view(request):
    try:
        response = requests.get(f'https://api.greenweb.com.bd/g_api.php?token={settings.SMS_API_TOKEN}&balance&expiry&json', timeout=10)
        sms_balance = response.json()[0]['response']
        sms_expiry_date = response.json()[1]['response']
    except requests.exceptions.RequestException:
        return JsonResponse({"message":"error"})

    context = {
        'balance':sms_balance,
        'expiry':sms_expiry_date,
    }
    return JsonResponse(context)



from .utils import monthly_bill_generator, user_import
def generate_bills(request):
    if monthly_bill_generator():
        return JsonResponse({"success":True, "message":"bill generated"})



#Previous Dues Updater month wise
@login_required
@user_passes_test(lambda user: user.is_superuser or user.is_admin)
def previous_bill_updater(request, id):
    preDues = int(request.POST.get('preDues', None)) # get total previous dues from user
    customer = get_object_or_404(Customer, id=id)
    monthly_charge = customer.monthlyCharge 
    permanent_discount = customer.permanentDiscount

    fraction_dues = preDues % (monthly_charge - permanent_discount) # get fraction dues from total dues
    total_month = int(preDues // (monthly_charge - permanent_discount))
    today = timezone.now().replace(day=1) # point current month

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
                permanentDiscount=permanent_discount,
                customer=customer
                )
            counter += 1 # increase counter

    return JsonResponse({'success':True,'message':'updated'})


