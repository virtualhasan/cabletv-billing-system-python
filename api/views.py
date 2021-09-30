import json
from django.conf import settings
import requests
from catv.views import customers
from catv.models import Area, Bill, Company, Customer, Payment
from django.http.response import Http404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers, status
from .serializers import AreaSerializer, BillSerializer, CustomerSerializer, CustomerUpdateSerializer, MakePaymentSerializer, PaymentSerializer
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction



class AreaList(APIView):
    permission_classes= [IsAuthenticated,]

    def get(self, request):
        area = Area.objects.all()
        serializer = AreaSerializer(area, many=True)
        return Response(serializer.data)
        
    def post(self, request):
        serializer = AreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

class AreaDetails(APIView):
    permission_classes= [IsAuthenticated,]


    def get_object(self, id):
        try:
            return Area.objects.get(id=id)
        except Area.DoesNotExist:
            raise Http404

    def get(self, request, id):
        area = self.get_object(id)
        serializer = AreaSerializer(area)
        return Response(serializer.data)

    def put(self,request, id):
        area = self.get_object(id)
        serializer = AreaSerializer(area, data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        area = self.get_object(id)
        area.delete()
        return Response({"message":"Deleted"}, status=status.HTTP_204_NO_CONTENT)



#Customer Views
class CustomerList(APIView):
    permission_classes= [IsAuthenticated,]


    def get(self, request):
        
        customer = Customer.objects.all()
        serializer = CustomerSerializer(customer, many=True)
        return Response(serializer.data)

    def post(self, request):
        print(request.data)

        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(createBy=request.user)
            return Response(serializer.data)
        return Response({"error":serializer.errors})

class CustomerDetails(APIView):
    permission_classes= [IsAuthenticated,]



    def get_object(self, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist as e:
            raise Http404

    def get(self, request, id):
        customer = self.get_object(id)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)


    def put(self, request, id):
        customer = self.get_object(id)
        serializer = CustomerUpdateSerializer(customer, request.data)
        if serializer.is_valid():
            serializer.save(updateBy=request.user)
            return Response(serializer.data)

        print(serializer.errors)
        return Response(serializer.errors)

    
    def delete(self, request, id):
        customer = self.get_object(id)
        customer.delete()
        return Response({'message':'deleted'})



class BillList(APIView):
    permission_classes= [IsAuthenticated,]


    def get(self,request):
        bills = Bill.objects.all()
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)

class BillDetails(APIView):
    permission_classes= [IsAuthenticated,]


    def get(self, request, id):
        try:
            bill = Bill.objects.get(id=id)
        except Bill.DoesNotExist:
            return Response({"message":"Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = BillSerializer(bill)
        return Response(serializer.data)

    def delete(self, request, id):
        try:
            bill = Bill.objects.get(id=id)
        except Bill.DoesNotExist:
            raise Http404
        bill.delete()
        return Response({"message":"succesfully deleted"})


class CustomerWiseBill(APIView):
    permission_classes= [IsAuthenticated,]


    def get(self, request, *args, **kwargs):
        id = kwargs["id"]
        bills = Bill.objects.filter(customer=id, isPaid=False)
        serializer = BillSerializer(bills, many=True)
        return Response(serializer.data)



class PaymentList(APIView):
    permission_classes= [IsAuthenticated,]


    def get(self, request):
        payments = Payment.objects.all()
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)


class CustomerWisePayment(APIView):
    permission_classes= [IsAuthenticated,]

    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    # permission_classes = [IsAuthenticated,]

    def get_object(self, id):
        try:
           customer = Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            raise Http404
        return customer


    def get(self,request, *agrs,**kwargs):
        id = kwargs['id']
        payments = Payment.objects.filter(customer=id)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data)

    #For Add Payment
    def post(self, request, id):
        customer = self.get_object(id)
        is_sms = request.data.pop('isSms')
        
       
        bills = request.data.pop('bills', [])
        bill_objects = [Bill.objects.get(id=new_bill_id, customer=id) for new_bill_id in bills]
        total_amount = self._get_total_amount(bill_objects)
        pre_dues = self._get_previous_dues(id)

        if self._check_paid(bills):
            return Response({"success":False, "message":"already paid"})


        serializer = MakePaymentSerializer(data=request.data)
        if serializer.is_valid():
            paid_amount = serializer.validated_data.get('paidAmount',0)
            discount = serializer.validated_data.get('discount',0)
            dues = total_amount - (paid_amount + discount)
            txnid = serializer.validated_data.get('txnId','')

            payment = Payment(**serializer.data)
            payment.totalAmount = total_amount
            payment.dues = dues + pre_dues
            payment.customer = customer
            payment.paidBy = request.user

            with transaction.atomic():
                payment.save()
                for bill_object in bill_objects:
                    bill_object.isPaid = True
                    bill_object.payment = payment
                    bill_object.save()
                company = Company.objects.last()
                if is_sms:
                    message = f'Dear User, {customer.id}. Your cable tv bill successfully paid. Amount {paid_amount} discount {discount} receipt {txnid}'
                    bangla_message= f'প্রিয় {customer.name}({customer.id}), {company.banglaName} বিল {paid_amount:.0f} টাকা {txnid} রসিদে পরিশোধ করা হয়েছে। বকেয়া {customer.get_total_dues():.0f} টাকা, Contact:{company.mobileNumber}'
                    try:
                        if customer.mobileNumber != '0' or customer.mobileNumber != '':
                            response = requests.post(
                                'http://api.greenweb.com.bd/api.php', 
                                data={
                                    'token': settings.SMS_API_TOKEN,
                                    'to':customer.mobileNumber,
                                    'message':bangla_message
                                }
                            )

                            print(response.text)
                    except:
                        pass
                        


                return Response({"success":True, "message":"payment successfull"})
        return Response(serializer.errors)


    def _check_paid(self,bills):
        for bill in bills:
            if Bill.objects.filter(id=bill, isPaid=True).exists():
                return True
        return False

    def _get_total_amount(self, bills):
        total_amount = 0 
        for bill in bills:
            total_amount += bill.monthlyCharge
        return total_amount

    def _get_previous_dues(self, customer_id):
        payment = Payment.objects.filter(customer=customer_id).last()
        if payment:
            dues = payment.dues
            return dues
        return 0

