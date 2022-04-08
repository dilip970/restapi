import sys
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.serializers import Serializer
import pharmacy
# models
from users import models
# serializers
from .serializers import (AdminSerializer, LocationSerializer, SpecializationsSerializerPOST, SpecializationsSerializerGET, 
SubSpecializationsSerializer, DoctorSerializer,PharmacySerializer,DiagnosticsSerializer, SpecializationsSerializerStatus,
TestSerializer, AdminPasswordSerializer, ActiveSpecializationsList, UpdateDoctorSerializer, DoctorStatusSerialize,
AddDoctorSerializer, CountriesSerializer, StatesSerializer, CitiesSerializer, PatientListSerializer, SpecializationsWiseDoctors,
CategorySerializerGET, CategorySerializerPOST, CategorySerializerStatus, AllCategoriesListSerializer,PharmacyProductSerializer,ProductSerializerStatus)
#rest framework
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes, throttle_classes
from rest_framework.permissions import BasePermission, IsAuthenticated, SAFE_METHODS, AllowAny
# custom token
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
import jwt
from datetime import datetime, timedelta
# rate limiting
from rest_framework.throttling import UserRateThrottle

from superadmin import serializers
from hashlib import md5
from six import ensure_binary

# responses
unathorizedResponse = {
    "status": False,
    "message": "Invalid Token"
}

responseUserNotFound = {
    'status': 400,
    'message' : 'login failed...!',
     'data' : {}
     }

def getPayload(request):
    try:
        authorization_header = request.headers.get('Authorization')
        access_token = authorization_header.split(' ')[1]
        payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return False


# for resgiter
@api_view(['POST'])
def Register(request):
    serializer = AdminSerializer(data = request.data)
    if not serializer.is_valid():
        print(serializer._errors)
        return Response(False)
    else:
        'password' in request.data
        text = request.data['password']
        password = (md5(ensure_binary(text)).hexdigest().lower())
        serializer.save(password=password)
        return Response(serializer.data)


@api_view(['POST'])
# @throttle_classes([UserRateThrottle])
def Login(request):
    email = request.data["email"]
    text = request.data["password"]
    password = (md5(ensure_binary(text)).hexdigest().lower())
    try:
        admin = models.SuperAdmin.objects.get(email = email, password = password)
        if admin is not None:
            refreshToken = RefreshToken.for_user(admin)
            accessToken = refreshToken.access_token
            accessToken.set_exp(lifetime=timedelta(days=1))
            decodeJTW = jwt.decode(str(accessToken), settings.SECRET_KEY, algorithms=["HS256"]);
            # add payload here!!
            decodeJTW['iat'] = '1590917498'
            decodeJTW['user'] = admin.email
            decodeJTW['role'] = 'admin'
            decodeJTW['date'] = datetime.now().strftime("%d-%m-%Y %I:%M:%S %p")
            #encode
            encoded = jwt.encode(decodeJTW, settings.SECRET_KEY, algorithm="HS256")

            data = decodeJTW
            token = {'token':encoded}
            data.update(token)

            return Response({
                'status': 200,
                'message' : 'login success...!',
                'data'     : {
                'user_data':[data]
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

class dashboardcount(APIView):
    def get(self,request):
        doctor = models.Doctor.objects.all()
        doctorcount = len(list(doctor))

        patient = models.Patient.objects.all()
        patientcount = len(list(patient))

        pharmacy = models.Pharmacy.objects.all()
        pharmacycount = len(list(pharmacy))

        product = models.Product.objects.all()
        productcount = len(list(product))

        diagnostics = models.Diagnostics.objects.all()
        diagnosticscount = len(list(diagnostics))

        test = models.Tests.objects.all()
        testcount = len(list(test))

        return Response({'status': "200",'message' : 'Dashboard count below','data' : {'count':["doctorcount",doctorcount,"patientcount",patientcount,"pharmacycount",pharmacycount,"productcount",productcount,"diagnosticscount",diagnosticscount,"testcount",testcount]}})

#SuperAdmin Changepassword 
#======================
password_status = {"status":"200", "message":"Password Changed Sucessfully", "data":{}}
oldpassword_error = {"status":"400", "message":"Oldpassword Is Incorrect", "data":{}}
confirm_error = {"status":"400", "message":"Newpassword and Confirm Password Not Matching", "data":{}}
oldnew_error = {"status":"400", "message":"Oldpassword and Newpassword Can't be Same", "data":{}}
class Change_Password(APIView):
    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        oldpassword = md5(ensure_binary(request.data["password"])).hexdigest()
        newpassword = md5(ensure_binary(request.data["newpassword"])).hexdigest()
        confirmpassword = md5(ensure_binary(request.data["confirmpassword"])).hexdigest()
        password_change = models.SuperAdmin.objects.get(id = payload['user_id'])
        serializer = AdminPasswordSerializer(password_change, data = request.data)
        if not serializer.is_valid():
            return Response(serializer.errors)
        elif models.SuperAdmin.objects.filter(id = payload['user_id'], password = oldpassword).exists():
            if oldpassword == newpassword:
                return Response(oldnew_error)
            elif newpassword == confirmpassword:
                serializer.save(password = newpassword)
                return Response(password_status)
            else:
                return Response(confirm_error)
        else:
            return Response(oldpassword_error)

#Patient in SUperAdmin
#=====================
class Patient_List(APIView):
    def get(self, request):
        patient = models.Patient.objects.all()
        serializer = PatientListSerializer(patient, many = True)
        return Response({'status': "200",'message' : 'patient list below','data' : {'patient_list':serializer.data}})


# Superadmin Locations GET  &  POST  &  EDIT  &&  Status Changing
# ===============================================================

class Countries(APIView):
    def get(self, request):
        countries = models.Country.objects.filter(status = 1)
        serializer = CountriesSerializer(countries, many = True)
        return Response({'status': "200",'message' : 'countries list below','data' : {'countries_list':serializer.data}})
        
class States(APIView):
    def get(self, request, id):
        if models.State.objects.filter(country = id).exists():
            states = models.State.objects.filter(status = 1, country = id)
            serializer = StatesSerializer(states, many = True)
            return Response({'status': "200",'message' : 'states list below','data' : {'states_list':serializer.data}})
        else:
            return Response({"status":"400", "message":"requested states data not available", "data":{}}) 
class Cities(APIView):
    def get(self, request, id):
        if models.City.objects.filter(state = id).exists():
            cities = models.City.objects.filter(status = 1, state = id)
            serializer = CitiesSerializer(cities, many = True)
            return Response({'status': "200",'message' : 'cities list below','data' : {'cities_list':serializer.data}})
        else:
            return Response({"status":"400", "message":"requested cities data not available", "data":{}})   

class Total_Countries(APIView):
    def get(self, request):
        countries = models.Country.objects.all()
        serializer = CountriesSerializer(countries, many = True)
        return Response({'status': "200",'message' : 'countries list below','data' : {'countries_list':serializer.data}})
        
class Total_States(APIView):
    def get(self, request):
        states = models.State.objects.all()
        serializer = StatesSerializer(states, many = True)
        return Response({'status': "200",'message' : 'states list below','data' : {'states_list':serializer.data}})
 
class Total_Cities(APIView):
    def get(self, request):
        cities = models.City.objects.all()
        serializer = CitiesSerializer(cities, many = True)
        return Response({'status': "200",'message' : 'cities list below','data' : {'cities_list':serializer.data}})

class add_locations(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        locations = models.Locations.objects.all()
        serializer = LocationSerializer(locations, many = True)
        return Response(serializer.data)

    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        location = LocationSerializer(data = request.data)
        if not location.is_valid():
            return Response(location._errors)
        else:
            location.save()
            return Response(location.data)
   
edit_locations_status = {"Location Details Updated Sucessfully"}
class edit_location(APIView):
    def get(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_404_NOT_FOUND)
        locations = models.Locations.objects.filter(id = id)
        serializer = LocationSerializer(locations, many = True)
        return Response(serializer.data)
    def post(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_404_NOT_FOUND)
        locations = models.Locations.objects.get(id = id)
        serializer = LocationSerializer(locations, data = request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(edit_locations_status, status = status.HTTP_200_OK)

location_sucess = {"status":"200", "message":"Location Status Changed Sucessfully"}
location_notfound = {"status":"404", "message":"Location Not Found"}
class location_status(APIView):
    """
    @param id
    @type subscpe || spec
    @return Response
    """
    def patch(self, request, id, format=None):
        # requestType = request.GET.get('type')
        # if requestType == 'location' and models.Locations.objects.filter(id=id).exists():
        if models.Locations.objects.filter(id=id).exists():
            location = models.Locations.objects.get(id=id)
            if location.status == 0:
                location.status = 1
                location.save()
                return Response(location_sucess, status.HTTP_200_OK)
            else:
                location.status = 0
                location.save()
                return Response(location_sucess, status.HTTP_200_OK)
        else:
            return Response(location_notfound, status.HTTP_404_NOT_FOUND)


# Superadmin Specializations GET & POST &  EDIT  &&  Status Changing
# ==================================================================
add_specialization = {"status":"200", "message":"specialization added successfully", "data":{}}
already_exists     = {"status":"400", "message":"specialization already exists", "data":{}}
class add_specializations(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        specializations = models.Specializations.objects.all()
        serializer = SpecializationsSerializerGET(specializations, many = True)
        return Response({'status': "200",'message' : 'specialization list below','data' : {'specialization_data':[serializer.data]}})
    
    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        specialization = request.data["specialization"]
        if models.Specializations.objects.filter(specialization=specialization).exists():
            return Response(already_exists)
        else:
            specialization = SpecializationsSerializerPOST(data = request.data)
            if not specialization.is_valid():
                return Response(specialization._errors)
            else:
                specialization.save()
                return Response(add_specialization)

class edit_specializations(APIView):
    def get(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        specializations = models.Specializations.objects.filter(id = id)
        serializer = SpecializationsSerializerGET(specializations, many = True)
        return Response(serializer.data)
    def post(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        if models.Specializations.objects.filter(specialization = request.data['specialization']).exclude(id = id):
            return Response(already_exists)
        else:
            specializations = models.Specializations.objects.get(id = id)
            serializer = SpecializationsSerializerPOST(specializations, data = request.data)
            if serializer.is_valid():
                serializer.save()
            return Response({'status': "200", "message":"specialization updated sucessfully", 'data' : {}})

specialization_status_sucess    =   {"status":"200", "message":"status changed sucessfully",'data' : {}}
specialization_status_error    =   {"status":"400", "message":"given data doesn't exists",'data' : {}}
class specializations_status(APIView):
    """
    @param id
    @type subscpe || spec
    @return Response
    """
    def post(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        if models.Specializations.objects.filter(id = id).exists():
            specialization = models.Specializations.objects.get(id = id)
            specialization = SpecializationsSerializerStatus(specialization,data = request.data)
            if not specialization.is_valid():
                return Response(specialization._errors)
            else:
                'status' in self.request.data
                status =self.request.data['status']
                specialization.save(status = status)
                return Response(specialization_status_sucess)
        else:
            return Response(specialization_status_error)


class Active_Specializations(APIView):
    def get(self, request, format = None):
        specializations = models.Specializations.objects.filter(status = 1)
        serializer = ActiveSpecializationsList(specializations, many = True)
        return Response({'status': "200",'message' : 'active specialization list','data' : {'specialization_data':[serializer.data]}})


# Superadmin Subspecializations GET  &  POST  &  EDIT  &&  Status Changing
# ========================================================================
class add_subspecializations(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        subspecializations = models.SubSpecializations.objects.all()
        serializer = SubSpecializationsSerializer(subspecializations, many = True)
        return Response(serializer.data)

    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        subspecialization = SubSpecializationsSerializer(data = request.data)
        if not subspecialization.is_valid():
            return Response(subspecialization._errors)
        else:
            subspecialization.save()
            return Response(subspecialization.data)


edit_subspecialization_status = {'status': "200", "message":"Subspecialization Updated Sucessfully"}
class edit_subspecializations(APIView):
    def get(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_404_NOT_FOUND)
        subspecializations = models.SubSpecializations.objects.filter(id = id)
        serializer = SubSpecializationsSerializer(subspecializations, many = True)
        return Response(serializer.data)
    def post(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_404_NOT_FOUND)
        subspecializations = models.SubSpecializations.objects.get(id = id)
        serializer = SubSpecializationsSerializer(subspecializations, data = request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(edit_subspecialization_status, status = status.HTTP_200_OK)


subspecialization_status_sucess = {"status":"200", "message":"SubSpecialization Status Changed Sucessfully"}
subspecialization_status_error = {"status":"404", "message":"User Not Exists"}
class subspecialization_status(APIView):
    """
    @param id
    @type subscpe || spec
    @return Response
    """
    def patch(self, request, id, format = None):
        # requestType = request.GET.get('type')
        # if requestType == 'subspecialization' and models.SubSpecializations.objects.filter(id=id).exists():
        if models.SubSpecializations.objects.filter(id=id).exists():
            subspecialization = models.SubSpecializations.objects.get(id=id)
            if subspecialization.status == 0:
                subspecialization.status = 1
                subspecialization.save()
                return Response(subspecialization_status_sucess)
            else:
                subspecialization.status = 0
                subspecialization.save()
                return Response(subspecialization_status_sucess)
        else:
            return Response(subspecialization_status_error)

# Superadmin Doctors GET  &  POST  &  EDIT  &&  Status Changing
# =============================================================
add_doctor = {"status":"200", "message":"doctor added successfully", "data":{}}
class add_doctors(APIView):
    def get(self, request, format = None):
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse)
        doctors = models.Doctor.objects.all()
        serializer = DoctorSerializer(doctors, many = True)
        return Response({'status': "200",'message' : 'doctor list below','data' : {'doctors_data':[serializer.data]}})

    def post(self, request, format = None):
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse)
        password = request.data["password"]
        confirmpassword = request.data["confirmpassword"]
        if password == confirmpassword:
            doctor = AddDoctorSerializer(data = request.data)
            if not doctor.is_valid():
                return Response(doctor._errors)
            else:
                'password' in self. request.data
                text =self.request.data['password']
                password = (md5(ensure_binary(text)).hexdigest().upper())
                doctor.save(password=password)
                return Response(add_doctor)
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse)
        subspecialization = AddDoctorSerializer(data = request.data)
        if not subspecialization.is_valid():
            return Response(subspecialization._errors)
        else:
            return Response({"status":"600", "message":"password and confirmpassword not matching", "data":{}})

class edit_doctor(APIView):
    def get(self, request, id, format = None):
        if models.Doctor.objects.filter(id = id).exists():
            doctor = models.Doctor.objects.filter(id = id)
            serializer = DoctorSerializer(doctor, many = True)
            return Response({'status': "200", 'message' : 'edit doctor details','data' : {'doctor_data':serializer.data}})
        else:
            return Response({'status': "400", 'message' : 'requested data not found','data' : {}})
    def post(self, request, id, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        if models.Doctor.objects.filter(email = request.data['email']).exclude(id = id):
            return Response({"status":"400", "message":"email id already exists", "data":{}})
        else:
            doctor = models.Doctor.objects.get(id = id)
            serializer = UpdateDoctorSerializer(doctor, data = request.data)
            if serializer.is_valid():
                serializer.save()
            return Response({"status":"200", "message":"doctor updated successfully", "data":{}})


doctor_success = {"status":"200", "message":"doctor status changed sucessfully",'data' : {}}
doctor_notfound ={"status":"400", "message":"given data doesn't exists",'data' : {}}
class doctor_status(APIView):
    def post(self,request,id,format=None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        if models.Doctor.objects.filter(id=id).exists():
            doctor = models.Doctor.objects.get(id=id)
            doctor = DoctorStatusSerialize(doctor,data = request.data)
            if not doctor.is_valid():
                return Response(doctor._errors)
            else:
                'status' in self.request.data
                status =self.request.data['status']
                doctor.save(status = status)
                return Response(doctor_success)
        else:
            return Response(doctor_notfound)

class specialization_doctors(APIView):
    def get(self, request, id):
        if models.Doctor.objects.filter(specialization = id, status =1).exists():
            doctors_specialization_wise = models.Doctor.objects.filter(specialization = id, status =1)
            serializer = SpecializationsWiseDoctors(doctors_specialization_wise,many = True)
            return Response({'status':'200', 'message':'specialization wise doctors list', 'data' : {'doctor_list':serializer.data}})
        else:
            return Response({'status':'400', 'message':'requested data not available', 'data' : {}})

# Superadmin Pharmacy GET  &  POST  &  EDIT  &&  Status Changing
# ==============================================================
pharmacy_addmsg = {'status':'200', 'message':'Pharmacy Details Added Successfully'}
class add_pharmacy(APIView):
    def get(self,request,format=None):
        # payload = getPayload(request)
        # if payload !=  False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        pharma = models.Pharmacy.objects.all()
        serializer = PharmacySerializer(pharma,many = True)
        return Response({'status': "200",'message' : 'pharmacy list below','data' : {'pharmacy_data':[serializer.data]}})
    
    def post(self,request, format = None):
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        pharma = PharmacySerializer(data = request.data)
        if not pharma.is_valid():
            return Response(pharma._errors,status=status.HTTP_404_NOT_FOUND)
        else:
            pharma.save()
            return Response(pharmacy_addmsg,status=status.HTTP_201_CREATED)
            

edit_pharmacy_status = {'status':'200', 'message':'Pharmacy Updated Sucessfully.'}
edit_pharmacy_error = {'status':'404', 'message':'Pharmacy Not Found.'}
class edit_pharmacy(APIView):
    def get(self, request, id, format=None):
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        if models.Pharmacy.objects.filter(id = id).exists():
            pharmacy = models.Pharmacy.objects.filter(id = id)
            serializer = PharmacySerializer(pharmacy, many = True)
            return Response(serializer.data)
        else:
            return Response(edit_pharmacy_error, status = status.HTTP_404_NOT_FOUND)
    def post(self, request, id, format = None):
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        if models.Pharmacy.objects.filter(id = id).exists():
            pharmacy = models.Pharmacy.objects.get(id = id)
            serializer = PharmacySerializer(pharmacy, data = request.data)
            if serializer.is_valid():
                serializer.save()
            return Response(edit_pharmacy_status, status = status.HTTP_200_OK)
        else:
            return Response(edit_pharmacy_error, status = status.HTTP_404_NOT_FOUND)


pharmacy_success = {"status":"200", "message":"Pharmacy Status Changed Sucessfully"}
pharmacy_notfound = {"status":"404", "message":"Pharmacy Not Found"}
class pharmacy_status(APIView):
    def patch(self,request,id,format=None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        # requestType = request.GET.get('type')
        # if requestType == 'Pharmacy' and models.Pharmacy.objects.filter(id=id).exists():

        if models.Pharmacy.objects.filter(id=id).exists():
            pharmacy = models.Pharmacy.objects.get(id=id)
            if pharmacy.status == 0:
                pharmacy.status = 1
                pharmacy.save()
                return Response(pharmacy_success,status=status.HTTP_200_OK)
            else:
                pharmacy.status = 0
                pharmacy.save()
                return Response(pharmacy_success,status.HTTP_200_OK)
        else:
            return Response(pharmacy_notfound)

# Add Categories Get & Edit & Status Change
#=========================================
already_exists     = {"status":"400", "message":"category already exists", "data":{}}
class add_category(APIView):
    def get(self, request, format = None):
        category = models.Categories.objects.filter(status = 1)
        serializer = CategorySerializerGET(category, many = True)
        return Response({'status': "200",'message' : 'category list below','data' : {'category_data':serializer.data}})
    
    def post(self, request, format = None):
        category_name = request.data["category_name"]
        if models.Categories.objects.filter(category_name=category_name).exists():
            return Response(already_exists)
        else:
            category = CategorySerializerPOST(data = request.data)
            if not category.is_valid():
                return Response(category._errors)
            else:
                category.save()
                return Response({"status":"200", "message":"category added successfully", "data":{}})


class edit_category(APIView):
    def get(self, request, id, format = None):
        category = models.Categories.objects.filter(id = id)
        serializer = CategorySerializerGET(category, many = True)
        return Response({'status': "200", 'message' : 'edit category details','data' : {'category_data':serializer.data}})
    def post(self, request, id, format = None):
        if models.Categories.objects.filter(category_name = request.data['category_name']).exclude(id = id):
            return Response(already_exists)
        else:
            category = models.Categories.objects.get(id = id)
            serializer = CategorySerializerPOST(category, data = request.data)
            if serializer.is_valid():
                serializer.save()
            return Response({'status': "200", "message":"category updated sucessfully", 'data' : {}})


category_status_sucess    =   {"status":"200", "message":"status changed sucessfully",'data' : {}}
category_status_error    =   {"status":"400", "message":"given data doesn't exists",'data' : {}}
class category_status(APIView):
    def post(self, request, id, format = None):
        if models.Categories.objects.filter(id = id).exists():
            category = models.Categories.objects.get(id = id)
            category = CategorySerializerStatus(category,data = request.data)
            if not category.is_valid():
                return Response(category._errors)
            else:
                'status' in self.request.data
                status =self.request.data['status']
                category.save(status = status)
                return Response(category_status_sucess)
        else:
            return Response(category_status_error)


class All_Categories(APIView):
    def get(self, request, format = None):
        category = models.Categories.objects.all()
        serializer = AllCategoriesListSerializer(category, many = True)
        return Response({'status': "200",'message' : 'all categories list','data' : {'categories_data':serializer.data}})


# Superadmin Diagnostics GET  &  POST  &  EDIT  &&  Status Changing
# ================================================================= 
diagnostics_addmsg = 'Diagnostics Details Added Successfully'
class add_diagnostics(APIView):
    def get(self,request,format=None):
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        diagnostics = models.Diagnostics.objects.all()
        serializer = DiagnosticsSerializer(diagnostics,many = True)
        return Response(serializer.data)
    
    def post(self,request, format = None):
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        diagnostics = DiagnosticsSerializer(data = request.data)
        if not diagnostics.is_valid():
            return Response(diagnostics._errors,status=status.HTTP_404_NOT_FOUND)
        else:
            diagnostics.save()
            return Response(diagnostics_addmsg,status=status.HTTP_201_CREATED)
edit_diagnostic_status = {"status":"200", "message":"Diagnostics Updated Sucessfully"}
class edit_diagnostics(APIView):
    def get(self, request, id, format = None):
        # payload = getPayload(request)
        # if payload != None:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse, status = status.HTTP_404_NOT_FOUND)
        diagnostic = models.Diagnostics.objects.filter(id = id)
        serializer = DiagnosticsSerializer(diagnostic, many = True)
        return Response(serializer.data)
    def post(self, request, id, format = None):
        # payload = getPayload(request)
        # if payload != False:
        #     print(payload)
        # else:
        #     return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        diagnostic = models.Diagnostics.objects.get(id = id)
        serializer = DiagnosticsSerializer(diagnostic, data = request.data)
        if serializer.is_valid():
            serializer.save()
        return Response(edit_diagnostic_status, status = status.HTTP_200_OK)

diagnostics_success = {'status':'200','message':'Diagnostics status changed successfully'}
diagnostics_notfound ={'status':'404','message':'Diagnostics Not Found'}
class diagnostics_status(APIView):
    def patch(self,request,id,format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        # requestType = request.GET.get('type')
        # if requestType == 'Diagnostics' and models.Diagnostics.objects.filter(id=id).exists():
        if models.Diagnostics.objects.filter(id=id).exists():
            diagnostics = models.Diagnostics.objects.get(id=id)
            if diagnostics.status == 0:
                diagnostics.status = 1
                diagnostics.save()
                return Response(diagnostics_success,status.HTTP_200_OK)
            else:
                diagnostics.status = 0
                diagnostics.save()
                return Response(diagnostics_success,status.HTTP_200_OK)
        else:
            return Response(diagnostics_notfound,status.HTTP_404_NOT_FOUND)

product_status_sucess    =   {"status":"200", "message":"status changed sucessfully",'data' : {}}
product_status_error    =   {"status":"400", "message":"given data doesn't exists",'data' : {}}
class Product_Status(APIView):
    def post(self, request, id, format = None):
        if models.Product.objects.filter(id = id).exists():
            product = models.Product.objects.get(id = id)
            product = ProductSerializerStatus(product,data = request.data)
            if not product.is_valid():
                return Response(product._errors)
            else:
                'status' in self.request.data
                status =self.request.data['status']
                product.save(status = status)
                return Response(product_status_sucess)
        else:
            return Response(product_status_error)




@api_view(['GET'])
def Checktoken(request):
    # authorization_heaader = request.headers.get('Authorization')
    # access_token = authorization_heaader.split(' ')[1]
    # payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=['HS256'])
    # print(payload)
    payload = getPayload(request)
    if (payload != False):
        print(payload)
    else:
        return Response(unathorizedResponse, status=status.HTTP_401_UNAUTHORIZED)
    admin = models.SuperAdmin.objects.all()
    serializer = AdminSerializer(admin, many = True)
    return Response(serializer.data)



class pharmacy_productslist(APIView):
    def get(self, request, id, format = None):
        if models.Product.objects.filter(id = id).exists():
            product = models.Product.objects.filter(pharmacy=id)
            serializer = PharmacyProductSerializer(product, many = True)
            return Response({'status': "200", 'message' : 'pharmacy products details','data' : {'pharmacy_products_data':serializer.data}})
        else:
            return Response({'status': "400", 'message' : 'requested data not found','data' : {}})
#==============================================================
#for website 
#==============================================================

#Doctors Details for website
#==============================================================
class doctor_details(APIView):
    def get(self,request,format=None):
        details = models.Doctor.objects.filter(status=1)
        serializer = DoctorSerializer(details,many = True)
        return Response({'status': "200",'message' : 'doctors list below','data' : {'doctors_data':[serializer.data]}})

doctorid_notfound ={'status':'404','message':'Requested Doctor ID is not found'}
class doctor_id_details(APIView):
    def get(self,request,id,format=None):
        if models.Doctor.objects.filter(id=id).exists():
            details = models.Doctor.objects.get(id=id)
            serializer = DoctorSerializer(details)
            return Response({'status': "200",'message' : 'doctors list ID wise','data' : {'doctors_id_data':[serializer.data]}})
        else:
            return Response(doctorid_notfound, status=status.HTTP_404_NOT_FOUND)

#Medicine Details for website
#==============================================================
class medicine_details(APIView):
    def get(self,request,format=None):
        details = models.Medicine.objects.all()
        serializer = MedicineSerializer(details,many = True)
        return Response({'status': "200",'message' : 'Medicine list','data' : {'allmedicine_data':[serializer.data]}})        

medicineid_notfound ={'status':'404','message':'Requested Diagnostics ID is not found'}
class medicine_id_details(APIView):
    def get(self,request,id,format=None):
        if models.Medicine.objects.filter(id=id).exists():
            details = models.Medicine.objects.get(id=id)
            serializer = MedicineSerializer(details)
            return Response({'status': "200",'message' : 'Medicine list ID wise','data' : {'medicine_id_data':serializer.data}})
        else:
            return Response(medicineid_notfound, status=status.HTTP_404_NOT_FOUND)

#Diagnostics Details for website
#==============================================================
class diagnostics_details(APIView):
    def get(self,request,format=None):
        details = models.Diagnostics.objects.all()
        serializer = DiagnosticsSerializer(details,many = True)
        return Response({'status': "200",'message' : 'Diagnostics list','data' : {'diagnostics_data':[serializer.data]}})

diagnosticsid_notfound ={'status':'404','message':'Requested Diagnostics ID is not found'}
class diagnostics_id_details(APIView):
    def get(self,request,id,format=None):
        if models.Diagnostics.objects.filter(id=id).exists():
            details = models.Diagnostics.objects.get(id=id)
            serializer = DiagnosticsSerializer(details)
            return Response({'status': "200",'message' : 'Diagnostics list ID wise','data' : {'diagnostics_id_data':[serializer.data]}})
        else:
            return Response(diagnosticsid_notfound, status=status.HTTP_404_NOT_FOUND)


#Pharmacy Details for website
#==============================================================
class pharmacy_details(APIView):
    def get(self,request,format=None):
        details = models.Pharmacy.objects.all()
        serializer = PharmacySerializer(details,many = True)
        return Response(serializer.data)

#Test Details for website
#==============================================================
class test_details(APIView):
    def get(self,request,format=None):
        details = models.Tests.objects.all()
        serializer = TestSerializer(details,many = True)
        return Response({'status': "200",'message' : 'Test list','data' : {'test_data':[serializer.data]}})

testid_notfound ={'status':'404','message':'Requested Test ID is not found'}
class test_id_details(APIView):
    def get(self,request,id,format=None):
        if models.Tests.objects.filter(id=id).exists():
            details = models.Tests.objects.get(id=id)
            serializer = TestSerializer(details)
            return Response({'status': "200",'message' : 'Test list ID wise','data' : {'test_id_data':[serializer.data]}})
        else:
            return Response(testid_notfound, status=status.HTTP_404_NOT_FOUND)
