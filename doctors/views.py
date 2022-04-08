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
from .serializers import DoctorRegisterSerializer, DoctorSerializer, DoctorProfilePictureSerializer, DoctorChangepasswordSerializer, DoctorsPatientlist, TimingsActivateSerializer, DoctorProfileUpdateSerializer, PatientReviewsSerializer
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

#Doctor Registration View Here
#=============================
register_msg ={'status':'200','message':'Doctor Registered Successfully....!'}
register_error = {'status':'400', 'message':'Doctor Email Already Exists....!'}
class Register(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format = None):
        data = models.Doctor.objects.all()
        serializer = DoctorSerializer(data=data, many= True)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.data)


    def post(self, request, format= None):
        email = request.data["email"]
        if models.Doctor.objects.filter(email=email).exists():
            return Response(register_error, status = status.HTTP_400_BAD_REQUEST)
        else:
            serializer = DoctorRegisterSerializer(data= request.data)
            if not serializer.is_valid():
                print(serializer.errors)
                return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
            else:
                'password' in self. request.data
                text =self.request.data['password']
                password = (md5(ensure_binary(text)).hexdigest().lower())
                serializer.save(password=password)
                return Response(register_msg,status = status.HTTP_201_CREATED)


#Doctor Login View Here
#======================
user_error = {"status":"401", "status":"User Not Found Please Enter Correct Details"}
@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    email = request.data["email"]
    text = request.data["password"]
    password = (md5(ensure_binary(text)).hexdigest().lower())

    if models.Doctor.objects.filter(email=email, password=password).exists():
        user = models.Doctor.objects.get(email = email, password= password)    
        if user is not None:

            refreshToken = RefreshToken.for_user(user)
            accessToken = refreshToken.access_token
            accessToken.set_exp(lifetime=timedelta(days=1))
            decodeJTW = jwt.decode(str(accessToken), settings.SECRET_KEY, algorithms=["HS256"]);

            # add payload here!!
            decodeJTW['id'] = user.id
            decodeJTW['iat'] = '1590917498'
            decodeJTW['user'] = user.email
            decodeJTW['role'] = 'doctor'
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


#Doctor Change Password View Starts Here
#=======================================
password_status = {"status":"200", "message":"Password Changed Successfully"}
oldpassword_error = {"status":"404", "message":"Oldpassword Is Incorrect"}
confirm_error = {"status":"406", "message":"Newpassword and Confirm Password Not Matching"}
oldnew_error = {"status":"404", "message":"Oldpassword and Newpassword Can't be Same"}
class doctor_changepassword(APIView):
    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        oldpassword = md5(ensure_binary(request.data['password'])).hexdigest()
        newpassword = md5(ensure_binary(request.data['newpassword'])).hexdigest()
        confirmpassword = md5(ensure_binary(request.data['confirmpassword'])).hexdigest()
        change_password = models.Doctor.objects.get(id = payload['id'])
        serializer = DoctorChangepasswordSerializer(change_password, data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif models.Doctor.objects.filter(password = oldpassword).exists():
            if oldpassword == newpassword:
                return Response(oldnew_error, status = status.HTTP_404_NOT_FOUND)
            elif newpassword == confirmpassword:
                serializer.save(password = newpassword)
                return Response(password_status, status = status.HTTP_200_OK)
            else:
                return Response(confirm_error, status = status.HTTP_406_NOT_ACCEPTABLE)
        else:
            return Response(oldpassword_error, status = status.HTTP_404_NOT_FOUND)

#Doctor Profile Picture Upload View Here
#=======================================
@api_view(['POST'])
def UploadProfilePicture(request):
    payload = getPayload(request)
    if( payload!= False):
        print(payload)
    else:
        return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
    doctor = models.Doctor.objects.get(id = payload["id"])
    doctor.profile_picture = request.FILES.get('image')
    doctor.save()
    return Response(responseUploadProfilePicture)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Checktoken(request):
    print(getPayload(request))
    admin = models.Doctor.objects.all()
    print(admin)
    serializer = DoctorRegisterSerializer(admin, many = True)
    return Response(serializer.data)


#Patient List Filtering based on Doctor ID
#=========================================
class doctor_patients(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        patient_list = models.Patient_Appoinments.objects.filter(doctor_id = payload['id'])
        serializer = DoctorsPatientlist(patient_list, many = True)
        return Response(serializer.data)


#Doctor Available Timings Visible  &  Timings Blocking
#=====================================================
addtime_msg = {"status":"200","message":"Timings Added Successfully"}
class timings_active(APIView):
    def post(self, request):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        time = self.request.data['slot_time']
        times = time.split(',')
        if isinstance(times, list):
            slot_timimg = []
            for time in times:
                self.request.data['slot_time'] = time
                serializer = TimingsActivateSerializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                slot_timimg.append(serializer)
            save_timings = [model.save(doctor_id = payload['id'], status=1) for model in slot_timimg]
            TimingsActivateSerializer(save_timings, many=True)
            return Response(addtime_msg, status = status.HTTP_200_OK)
        serializer = TimingsActivateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

# blocktime_msg = {"status":"200","message":"Timings Blocked Successfully"}
# class timings_deactive(APIView):
#     def post(self,request):
#         payload = getPayload(request)
#         if payload != False:
#             print(payload)
#         else:
#             return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
#         time = self.request.data['slot_time']
#         times = time.split(',')
#         if isinstance(times, list):
#             slot_timimg = []
#             for time in times:
#                 self.request.data['slot_time'] = time+":"+"00"+"."+"000000"
#                 serializer = TimingsActivateSerializer(data=request.data)
#                 serializer.is_valid(raise_exception=True)
#                 slot_timimg.append(serializer)
#             save_timings = [model.save(doctor_id = payload['id'], status=0) for model in slot_timimg]
#             TimingsActivateSerializer(save_timings, many=True)
#             return Response(blocktime_msg, status = status.HTTP_200_OK)
#         serializer = TimingsActivateSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#Doctor Profile Update View Starts Here
#======================================
doctor_update = {'status':'200', 'message': 'Doctor Data Updated Sucessfully'}
doctor_fill   = {'status':'404', 'message': 'Please Provide the Updating Fields'}
doctor_notfound = {'status':'404', 'message': 'Requested Doctor Not Found'}
class edit_profiledetails(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
        doctor_profile = models.Doctor.objects.get(id = payload['id'])
        serializer = DoctorProfileUpdateSerializer(doctor_profile)
        return Response(serializer.data)

    
    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        doctor_profile = models.Doctor.objects.get(id = payload['id'])
        serializer = DoctorProfileUpdateSerializer(doctor_profile, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(doctor_update, status = status.HTTP_200_OK)
        return Response(doctor_fill, status=status.HTTP_404_NOT_FOUND)

#Doctor Reviews From Patient view Starts Here
#============================================
class patient_reviews(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        reviews = models.Patient_Reviews.objects.filter(doctor = payload['id'])
        serializer = PatientReviewsSerializer(reviews, many = True)
        return Response(serializer.data)
