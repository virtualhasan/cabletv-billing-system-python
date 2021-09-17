from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    #Area
    path('area/', views.AreaList.as_view(), name="area" ),
    path('area/<int:id>/', views.AreaDetails.as_view(), name='area_update'),

    #Customer
    path('customers/', views.CustomerList.as_view(), name="customers_list"),
    path('customers/<int:id>/', views.CustomerDetails.as_view(), name='customers_details'),

    #Bill
    path('bills/', views.BillList.as_view(), name="bills_list"),
    path("bills/<int:id>/", views.BillDetails.as_view(), name="bills_details"),
    path('customers/<int:id>/bills/', views.CustomerWiseBill.as_view(), name='customer_wise_bills'),

    #Payments
    path('payments/', views.PaymentList.as_view(), name='payments_list'),
    path('customers/<int:id>/payments/', views.CustomerWisePayment.as_view(), name='customer_wise_payment_list'),
]
