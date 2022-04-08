import sys
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
import json
import datetime as dt

from rest_framework.throttling import UserRateThrottle
# models
from users import models
# serializers
from .serializers import PatientRegisterSerializer, PatientProfileUpdateSerializer, PatientConsultSerializer,PatientLabAppointmentSerializer, PatientOrderSerializer, PatientTestOrderSerializer, PatientTicketSerializer,PatientCartSerializer, PatientPasswordSerializer,UsersRegisterSerializer
# rest framework
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes, throttle_classes
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS, AllowAny
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
# custom token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from hashlib import md5, new
from six import ensure_binary
import uuid

from users import serializers
from datetime import datetime, timedelta

# Create your views here.
class ReadOnly(BasePermission):
    SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS', 'POST']
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS

def getPayload(request):
    try:
        authorization_header = request.headers.get('Authorization')
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return False

# responses
unathorizedResponse = {
    "status": "401",
    "message": "Invalid Token"
}

responseUserNotFound = {
    'status': 400,
    'message' : 'login failed...!',
     'data' : {}
     }


# Patient Register View
# =========================
register_msg ={'status':'200','message':'patient registered successfully', "data":{}}
register_error = {"status":"400", "message":"patient email already exists", "data":{}}
class Register(APIView):
    permission_classes = [AllowAny]
    # throttle_scope = 'patient_auth'
    def post(self, request, format= None):
        password  = request.data['password']
        confirmpassword = request.data['confirmpassword']
        if password == confirmpassword:
            email = request.data['email']
            if models.Patient.objects.filter(email = email).exists():
                return Response(register_error)
            else:
                serializer = PatientRegisterSerializer(data= request.data)
                if not serializer.is_valid():
                    print(serializer.errors)
                    return Response(serializer.errors)
                else:
                    'password' in self.request.data
                    text = self.request.data['password']
                    password = (md5(ensure_binary(text)).hexdigest().lower())
                    serializer.save(password=password)
                    return Response(register_msg)
        else:
            return Response({"status":"600", "message":"password and confirmpassword not matching", "data":{}})    

    def get(self,request,format=None):
        payload = getPayload(request)
        if (payload != False):
            print(payload)
        else:
            return Response(unathorizedResponse)
        data = models.Patient.objects.all()
        serializer = PatientRegisterSerializer(data=data, many= True)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.data)

# Patient Login View
# =========================
@api_view(['POST'])
@permission_classes([AllowAny])
# @throttle_classes([UserRateThrottle])
def Login(request):
    email = request.data["email"]
    text = request.data["password"]
    password = (md5(ensure_binary(text)).hexdigest().lower())

    try:
        user = models.Patient.objects.get(email = email, password= password)    
        if user is not None:

            refreshToken = RefreshToken.for_user(user)
            accessToken = refreshToken.access_token
            accessToken.set_exp(lifetime=timedelta(days=1))
            decodeJTW = jwt.decode(str(accessToken), settings.SECRET_KEY, algorithms=["HS256"]);

            # add payload here!!
            decodeJTW['id'] = user.id
            decodeJTW['iat'] = '1590917498'
            decodeJTW['user'] = user.email
            decodeJTW['role'] = 'patient'
            decodeJTW['date'] = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")

            #encode
            encoded = jwt.encode(decodeJTW, settings.SECRET_KEY, algorithm="HS256")

            data = decodeJTW
            token = {'token':encoded}
            data.update(token)

            return Response({
                'status': 200,
                'message' : 'login success...!',
                'data'     : {
                'patient_details':[data]
                }

            })

        else:
            return Response(responseUserNotFound)

    except Exception as e :
        exception_type, exception_object, exception_traceback = sys.exc_info()
        line_number = exception_traceback.tb_lineno
        print("ERROR",e)
        print("Line number: ", line_number)
        return Response(responseUserNotFound)

#Patient Changepassword 
#======================
password_status     = {"status":"200", "message":"Password Changed Sucessfully", "data":{}}
oldpassword_error   = {"status":"400", "message":"Oldpassword Is Incorrect", "data":{}}
confirm_error       = {"status":"400", "message":"Newpassword and Confirm Password Not Matching", "data":{}}
oldnew_error        = {"status":"400", "message":"Oldpassword and Newpassword Can't be Same", "data":{}}
class patient_change_password(APIView):
    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        oldpassword = md5(ensure_binary(request.data["password"])).hexdigest()
        newpassword = md5(ensure_binary(request.data["newpassword"])).hexdigest()
        confirmpassword = md5(ensure_binary(request.data["confirmpassword"])).hexdigest()
        password_change = models.Patient.objects.get(id = payload['id'])
        serializer = PatientPasswordSerializer(password_change, data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)
        elif models.Patient.objects.filter(id = payload['id'], password = oldpassword).exists():
            if oldpassword == newpassword:
                return Response(oldnew_error)
            elif newpassword == confirmpassword:
                serializer.save(password = newpassword)
                return Response(password_status)
            else:
                return Response(confirm_error)
        else:
            return Response(oldpassword_error)


# Patient Profile Update View  GET  &  POST
#==========================================
class patientprofile_update(APIView):
    def get(self,request):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        profile_data = models.Patient.objects.get(id = payload["id"])
        serializer = PatientProfileUpdateSerializer(profile_data)
        return Response({'status': "200", 'message' : 'edit patient details','data' : {'patient_details':serializer.data}})
        
    def post(self, request):
        payload = getPayload(request)
        if (payload != False):
            print(payload)
        else:
            return Response(unathorizedResponse)

        if models.Patient.objects.filter(email = request.data['email']).exclude(id = payload["id"]):
            return Response({"status":"400", "message":"patient email already exists", "data":{}})
        else:            
            patient = models.Patient.objects.get(id = payload["id"])
            serializer = PatientProfileUpdateSerializer(patient, data=request.data)
            if serializer.is_valid():
                serializer.save()
            return Response({"status":"200", "message":"patient updated successfully", "data":{}})
            # return Response(serializer._errors)



#Patient Lab Appointment view ---- GET  and  POST
#============================================
testid_status = {'status':'200','message':'Test ID Created Sucessfully'}
class patient_lab_appointment(APIView):
    def get(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)        
        drappointment = models.Patient_Lab_Appointments.objects.filter(patient_id = payload['id'])
        serializer = PatientLabAppointmentSerializer(drappointment, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PatientLabAppointmentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif (payload['id'] in self.request.data):
            id = uuid.uuid1()
            test_id = id.fields
            test_id = "T"+str(test_id[0])
            # text = self.request.data["appointment_id"]
            # text = l
            serializer.save(test_id = test_id)
            return Response(testid_status, status=status.HTTP_200_OK)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        

#Patient Appointment view ---- GET  and  POST
#============================================
appointment_status ={'status':'200','message':'Appoinment Created Sucessfully'}
class patient_appointment(APIView):
    def get(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        appointment = models.Patient_Appoinments.objects.filter(patient_id = payload['id'])
        serializer = PatientConsultSerializer(appointment, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PatientConsultSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif (payload['id'] in self.request.data):
            id = uuid.uuid1()
            appointment_id = id.fields
            appointment_id = "A"+str(appointment_id[0])
            # text = self.request.data["appointment_id"]
            # text = l
            serializer.save(appointment_id = appointment_id)
            return Response(appointment_status, status=status.HTTP_200_OK)
        else:
            id = uuid.uuid1()
            appointment_id = id.fields
            appointment_id = "A"+str(appointment_id[0])
            serializer.save(appointment_id = appointment_id)
            return Response(serializer.data, status=status.HTTP_200_OK)



#Patient Order view ---- GET  &  POST  &  DELETE
#===============================================
order_status = {'status':'200', 'message': 'Your Order is Sucessfully'}
class patient_order(APIView):
    def get(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        orders = models.Patient_Orders.objects.filter(patient_id = payload['id'])
        serializer = PatientOrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PatientOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif (payload['id'] in self.request.data):
            id = uuid.uuid1()
            order_id = id.fields
            order_id = "P"+str(order_id[0])
            # text = self.request.data["order_id"]
            # text = l
            serializer.save(order_id = order_id)
            return Response(order_status, status=status.HTTP_200_OK)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

delete_sucess = {'status' : '200','message': 'Sucessfully Deleted'}
delete_unsucess = {'status' : '404','message': 'Requested Delete Content Not Found'}
@api_view(['DELETE'])
def delete_order(request, id):
    payload = getPayload(request)
    if( payload!= False):
        print(payload)
    else:
        return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)    
    if models.Patient_Orders.objects.filter(id=id).exists():
        order = models.Patient_Orders.objects.get(id=id)
        order.delete()
        return Response(delete_sucess, status=status.HTTP_200_OK)
    else:
        return Response(delete_unsucess, status=status.HTTP_404_NOT_FOUND)



#Patient Order Test view ---- GET  &  POST  &  DELETE
#===================================================
sucess_msg = {'status' : '200','message': 'Test Added Sucessfully'}
class patientorder_test(APIView):
    def get(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        tests = models.Patient_Lab_Appointments.objects.filter(patient_id = payload['id'])
        serializer = PatientTestOrderSerializer(tests, many=True)
        return Response(serializer.data)

    def post(self,request,format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PatientTestOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif (payload['id'] in self.request.data):
            id = uuid.uuid1()
            test_id = id.fields
            test_id = "T"+str(test_id[0])
            # text = self.request.data["test_id"]
            # text = l
            serializer.save(test_id = test_id)
            return Response(sucess_msg, status=status.HTTP_200_OK)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        

@api_view(['DELETE'])
def delete_test(request,id):
    payload = getPayload(request)
    if( payload!= False):
        print(payload)
    else:
        return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
    if models.Patient_Lab_Appointments.objects.filter(id=id).exists():
        tests = models.Patient_Lab_Appointments.objects.get(id=id)
        tests.delete()
        return Response(delete_sucess,status=status.HTTP_200_OK)
    else:
        return Response(delete_unsucess,status=status.HTTP_404_NOT_FOUND)


#Patient Ticket view ---- GET  &  POST
#=====================================
ticket_status = {'status':'200', 'message': 'Ticket Raised Sucessfully'}
class patient_ticket(APIView):
    def get(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)        
        tickets = models.Patient_Tickets.objects.filter(patient_id = payload['id'])
        serializer = PatientTicketSerializer(tickets, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PatientTicketSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif (payload['id'] in self.request.data):
            id = uuid.uuid1()
            ticket_id = id.fields
            ticket_id = "PT"+str(ticket_id[0])
            # text = self.request.data["ticket_id"]
            # text = l
            serializer.save(ticket_id = ticket_id)
            return Response(ticket_status, status=status.HTTP_200_OK)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

#  Patient Diagnostics Add Cart  GET  &  POST
# ===========================================
diagnostics_status = {'status':'200', 'message': 'Test Added to Your Cart'}
# diagnostics_msg = {'status':'404', 'message': 'User Data Not Found'}
class patient_diagnostics_cart(APIView):
    def get(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)        
        diagnostics = models.Patient_Cart.objects.filter(patient_id = payload["id"])
        test_cart = []
        for k in diagnostics:
            if k.type == "Test":
                test_cart.append(k)
            else:
                pass
        serializer = PatientCartSerializer(test_cart, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PatientCartSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif (payload["id"] in self.request.data):
            serializer.save(type = "Test")
            return Response(diagnostics_status, status=status.HTTP_200_OK)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)


#  Patient Pharmacy Add Cart  GET  &  POST
# ===========================================
pharmacy_status = {'status':'200', 'message': 'Medicine Added to Your Cart'}
# pharmacy_msg = {'status':'404', 'message': 'User Data Not Found'}
class patient_pharmacy_cart(APIView):
    def get(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)        
        medicine = models.Patient_Cart.objects.filter(patient_id = payload["id"])
        diagnostics_cart = []
        for k in medicine:
            if k.type == "Pharmacy":
                diagnostics_cart.append(k)
            else:
                pass
        serializer = PatientCartSerializer(diagnostics_cart, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        payload = getPayload(request)
        if( payload!= False):
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        serializer = PatientCartSerializer(data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif (payload["id"] in self.request.data):
            serializer.save(type="Pharmacy")
            return Response(pharmacy_status, status=status.HTTP_200_OK)
        else:
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)