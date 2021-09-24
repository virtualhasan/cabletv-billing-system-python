
from django.urls import path, include
from . import views
import debug_toolbar

urlpatterns = [
    path('', views.index, name='index'),
   
    path('customers/', views.customers, name='customers_list'),
    path('customers/add/', views.add_customers, name='add_customers'),
    path('customers/name_or_mobile/', views.customers_by_name_or_mobile, name='customers_by_name_or_mobile'),
    path('customers/<int:id>/inactive/', views.customer_inactive, name='customer_inactive'),
    path('customers/next_id/<int:area_id>/', views.get_next_id, name='next_id'),

    path('previous_bill_updater/<int:id>/', views.previous_bill_updater, name='bill_updater'),
    
   
    path('bills/', views.bills, name='bills_list'),

    path('reports/', views.reports, name='reports_list'),
    path('single_report/', views.single_report, name='single_report'),
    path('area_report/', views.area_report, name='area_report'),
    path('monthly_report/', views.monthly_report, name='monthly_report'),
    path('user_report/', views.user_report_view, name='user_report'),
    
    path('settings/', views.settings_view, name='settings'),
    path('sms_check/', views.sms_check_view, name='sms_check'),

    path('generate_bills/', views.generate_bills, name="generate_bills"),


    path('__debug__/', include(debug_toolbar.urls)),
]