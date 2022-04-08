# django settings
from users.views import patient_order
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
import json
import datetime as dt

from rest_framework.serializers import Serializer
# models
from users import models, serializers
# serializers
from .serializers import DiagnosticsRegisterSerializer, DiagnosticsChangepasswordSerializer, DiagnosticsProfileSerializer, DiagnosticsProfileEditSerializer, DiagnosticsReviewsSerializer,TestSerializer
#rest framework
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes, authentication_classes
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS, AllowAny
from rest_framework.authentication import TokenAuthentication, BasicAuthentication
# custom token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from hashlib import md5
from six import ensure_binary
from datetime import datetime, timedelta


# Create your views here.

class ReadOnly(BasePermission):
    SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS', 'POST']
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


def getPayload(request):
    try:
        authorization_heaader = request.headers.get('Authorization')
        access_token = authorization_heaader.split(' ')[1]
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return False

# responses
unathorizedResponse = {
    "status": False,
    "message": "Invalid Token"
}

responseUploadProfilePicture = {
    "status": True,
    "message": "uploaded successfully"
} 

responseUserNotFound = {
    'status': 400,
    'message' : 'login failed...!',
     'data' : {}
     }

#Registration View Here
#=============================
register_msg ={'status':'200','message':'Diagnostics Registered Successfully'}
register_error = {'status':'400', 'message':'Diagnostics Email Already Exists....!'}
class Register(APIView):
    permission_classes = [AllowAny]
    def post(self, request, format= None):
        email = request.data["email"]
        if models.Diagnostics.objects.filter(email=email).exists():
            return Response(register_error, status.HTTP_400_BAD_REQUEST)
        else:
            serializer = DiagnosticsRegisterSerializer(data= request.data)
            if not serializer.is_valid():
                print(serializer.errors)
                return Response(serializer.errors,status.HTTP_400_BAD_REQUEST)
            else:
                'password' in self. request.data
                text =self.request.data['password']
                password = (md5(ensure_binary(text)).hexdigest().lower())
                serializer.save(password=password)
                return Response(register_msg,status.HTTP_201_CREATED)            

#Login View Here
#======================
user_error = {'status': 400, 'message' : 'login failed...!', 'data' : {}}
@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    email = request.data["email"]
    text = request.data["password"]
    password = md5(ensure_binary(text)).hexdigest().lower()
    if models.Diagnostics.objects.filter(email=email, password=password).exists():
        user = models.Diagnostics.objects.get(email = email, password= password)

        if user is not None:
            refreshToken = RefreshToken.for_user(user)
            accessToken = refreshToken.access_token
            accessToken.set_exp(lifetime=timedelta(days=1))
            decodeJTW = jwt.decode(str(accessToken), settings.SECRET_KEY, algorithms=["HS256"]);

            # add payload here!!
            decodeJTW['id'] = user.id
            decodeJTW['iat'] = '1590917498'
            decodeJTW['user'] = user.email
            decodeJTW['role'] = 'diagnostics'
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
                'pharmacy_details':[data]
                }
            })
    else:
        return Response(responseUserNotFound)

#Change Password View Starts Here
#=======================================
password_status     =   {"status":"200", "message":"Password Changed Successfully"}
oldpassword_error   =   {"status":"404", "message":"Oldpassword Is Incorrect"}
confirm_error       =   {"status":"406", "message":"Newpassword and Confirm Password Not Matching"}
oldnew_error        =   {"status":"404", "message":"Oldpassword and Newpassword Can't be Same"}
class change_password(APIView):
    def post(self, request, format=None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        oldpassword     =   md5(ensure_binary(request.data['password'])).hexdigest()
        newpassword     =   md5(ensure_binary(request.data['newpassword'])).hexdigest()
        confirmpassword =   md5(ensure_binary(request.data['confirmpassword'])).hexdigest()
        change_password =   models.Diagnostics.objects.get(id = payload['id'])
        serializer      =   DiagnosticsChangepasswordSerializer(change_password, data  =   request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif models.Diagnostics.objects.filter(id = payload['id'], password =   oldpassword).exists():
            if oldpassword  ==  newpassword:
                return Response(oldnew_error, status = status.HTTP_404_NOT_FOUND)
            elif newpassword    ==  confirmpassword:
                serializer.save(password = newpassword)
                return Response(password_status, status = status.HTTP_200_OK)
            else:
                return Response(confirm_error, status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(oldpassword_error, status = status.HTTP_404_NOT_FOUND)

#Profile Update View Starts Here
#===============================
diagnostics_update = {'status':'200', 'message': 'Diagnostics Data Updated Sucessfully'}
diagnostics_fill   = {'status':'404', 'message': 'Please Provide the Updating Fields'}
class profile_update(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        diagnostics    =   models.Diagnostics.objects.get(id = payload['id'])
        serializer  =   DiagnosticsProfileSerializer(diagnostics)
        return Response(serializer.data)
    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        diagnostics = models.Diagnostics.objects.get(id = payload['id'])
        serializer = DiagnosticsProfileEditSerializer(diagnostics, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(diagnostics_update, status = status.HTTP_200_OK)
        return Response(diagnostics_fill, status = status.HTTP_404_NOT_FOUND)

# Diagnostics Tests GET  &  POST  &  EDIT  &&  Status Changing
# ===========================================================
tests_status = 'Tests Details Added Successfully'
class add_tests(APIView):
    def get(self,request,format=None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse,status=status.HTTP_401_UNAUTHORIZED)
        tests = models.Tests.objects.all()
        serializer = TestSerializer(tests,many =True)
        return Response(serializer.data)
    
    def post(self,request,format=None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse,status = status.HTTP_401_UNAUTHORIZED)
        tests = TestSerializer(data = request.data)
        if not tests.is_valid():
            return Response(tests._errors,status=status.HTTP_404_NOT_FOUND)
        else:
            tests.save()
            return Response(tests_status,status=status.HTTP_201_CREATED)
edit_test_status = {"status":"200", "message":"Test Updated Sucessfully"}
class edit_test(APIView):
    def get(self, request, id, format = None):
        payload =getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        test = models.Tests.objects.filter(id = id)
        serializer = TestSerializer(test, many = True)
        return Response(serializer.data)
    def post(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        test = models.Tests.objects.get(id = id)
        serializer = TestSerializer(test, data = request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(edit_test_status, status = status.HTTP_200_OK)

test_success = {'status':'200','message':'Test status changed successfully'}
test_notfound ={'status':'404','message':'Test Not Found'}
class test_status(APIView):
    def patch(self,request,id,format = None):
        # requestType = request.GET.get('type')
        # if requestType == 'Tests' and models.Tests.objects.filter(id=id).exists():
        if models.Tests.objects.filter(id=id).exists():
            test = models.Tests.objects.get(id=id)
            if test.status == 0:
                test.status = 1
                test.save()
                return Response(test_success,status.HTTP_200_OK)
            else:
                test.status = 0
                test.save()
                return Response(test_success,status.HTTP_200_OK)
        else:
            return Response(test_notfound,status.HTTP_404_NOT_FOUND)


# #Diagnostics Reviews From Patient view Starts Here
# #============================================
class diagnostics_reviews(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        reviews = models.Diagnostics_Reviews.objects.filter(diagnostics = payload['id'])
        serializer = DiagnosticsReviewsSerializer(reviews, many = True)
        return Response(serializer.data)    