# django settings
import pharmacy
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
from .serializers import (PharmacySerializer, PharmacyRegisterSerializer, PharmacyChangepasswordSerializer, 
PharmacyProfileSerializer, PharmacyProfileEditSerializer, PharmacyReviewsSerializer, AddProductSerializer,
UpdateProductSerializer, ProductSerializerStatus,AllCategoriesListSerializer,All_ProductsListSerializer,CategoryProductslistSerializer,ProductViewSerializer)
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
register_msg ={'status':'200','message':'Pharmacy Registered Successfully'}
register_error = {'status':'400', 'message':'Pharmacy Email Already Exists....!'}
class Register(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format = None):
        data = models.Pharmacy.objects.all()
        serializer = PharmacySerializer(data=data, many= True)
        if serializer.is_valid():
            return Response(serializer.data)
        else:
            return Response(serializer.data)


    def post(self, request, format= None):
        email = request.data["email"]
        if models.Pharmacy.objects.filter(email = email).exists():
            return Response(register_error, status = status.HTTP_400_BAD_REQUEST)
        else:
            serializer = PharmacyRegisterSerializer(data= request.data)
            if not serializer.is_valid():
                print(serializer.errors)
                return Response(serializer.errors,status = status.HTTP_400_BAD_REQUEST)
            else:
                'password' in self. request.data
                text =self.request.data['password']
                password = (md5(ensure_binary(text)).hexdigest().lower())
                serializer.save(password=password)
                return Response(register_msg,status = status.HTTP_201_CREATED)
    

#Login View Here
#======================
user_error = {"status":"401", "status":"User Not Found Please Enter Correct Details"}
@api_view(['POST'])
@permission_classes([AllowAny])
def Login(request):
    email = request.data["email"]
    text = request.data["password"]
    password = (md5(ensure_binary(text)).hexdigest().lower())

    if models.Pharmacy.objects.filter(email=email, password=password).exists():
        user = models.Pharmacy.objects.get(email = email, password= password)    
        if user is not None:

            refreshToken = RefreshToken.for_user(user)
            accessToken = refreshToken.access_token
            accessToken.set_exp(lifetime=timedelta(days=1))
            decodeJTW = jwt.decode(str(accessToken), settings.SECRET_KEY, algorithms=["HS256"]);

            # add payload here!!
            decodeJTW['id'] = user.id
            decodeJTW['iat'] = '1590917498'
            decodeJTW['user'] = user.email
            decodeJTW['role'] = 'pharmacy'
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
            return Response(unathorizedResponse)
        oldpassword     =   md5(ensure_binary(request.data['password'])).hexdigest()
        newpassword     =   md5(ensure_binary(request.data['newpassword'])).hexdigest()
        confirmpassword =   md5(ensure_binary(request.data['confirmpassword'])).hexdigest()
        change_password =   models.Pharmacy.objects.get(id = payload['id'])
        serializer      =   PharmacyChangepasswordSerializer(change_password, data  =   request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        elif models.Pharmacy.objects.filter(id = payload['id'], password =   oldpassword).exists():
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
pharmacy_update = {'status':'200', 'message': 'Pharmacy Data Updated Sucessfully'}
pharmacy_fill   = {'status':'404', 'message': 'Please Provide the Updating Fields'}
class profile_update(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        pharmacy    =   models.Pharmacy.objects.get(id = payload['id'])
        serializer  =   PharmacyProfileSerializer(pharmacy)
        return Response(serializer.data)
    def post(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        pharmacy = models.Pharmacy.objects.get(id = payload['id'])
        serializer = PharmacyProfileEditSerializer(pharmacy, data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(pharmacy_update, status = status.HTTP_200_OK)
        return Response(pharmacy_fill, status = status.HTTP_404_NOT_FOUND)

#Pharmacy Reviews From Patient view Starts Here
#============================================
class pharmacy_reviews(APIView):
    def get(self, request, format = None):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse, status = status.HTTP_401_UNAUTHORIZED)
        reviews = models.Pharmacy_Reviews.objects.filter(pharmacy = payload['id'])
        serializer = PharmacyReviewsSerializer(reviews, many = True)
        return Response(serializer.data)

#Prdoct Add & Edit & Status
# =========================
class Add_Product(APIView):
    def get(self, request):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        products = models.Product.objects.filter(pharmacy = payload['id'], status = 1)
        serializer = AddProductSerializer(products, many = True)
        return Response({'status': "200",'message' : 'products list below','data' : {'products_data':serializer.data}})
    def post(self, request):
        payload = getPayload(request)
        if payload != False:
            print(payload)
        else:
            return Response(unathorizedResponse)
        if models.Product.objects.filter(product_name = request.data["product_name"]).exists():
            return Response({"status":"400", "message":"product already exists", "data":{}})
        else:
            product = AddProductSerializer(data = request.data)
            if not product.is_valid():
                return Response(product._errors)
            else:
                import uuid
                product_id = "P"+str(uuid.uuid4()).upper()[:8]
                pharmacy = models.Pharmacy.objects.get(id = payload['id'])
                product.save(product_code = product_id, pharmacy = pharmacy)
                return Response({"status":"200", "message":"product added successfully", "data":{}})

class Edit_Product(APIView):
    def get(self, request, id, format = None):
        product = models.Product.objects.filter(id = id)
        serializer = AddProductSerializer(product, many = True)
        return Response({'status': "200", 'message' : 'edit product details','data' : {'product_details':serializer.data}})
    def post(self, request, id, format = None):
        if models.Product.objects.filter(product_name = request.data["product_name"]).exclude(id = id):
            return Response({"status":"400", "message":"product already exists", "data":{}})
        else:
            product = models.Product.objects.get(id = id)
            serializer = UpdateProductSerializer(product, data = request.data)
            if serializer.is_valid():
                serializer.save()
            return Response({'status': "200", "message":"product updated sucessfully", 'data' : {}})

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

class All_Categories(APIView):
    def get(self, request, format = None):
        category = models.Categories.objects.filter(status=1)
        serializer = AllCategoriesListSerializer(category, many = True)
        return Response({'status': "200",'message' : 'all categories list','data' : {'categories_data':serializer.data}})

class category_productslist(APIView):
    def get(self, request, id, format = None):
        if models.Categories.objects.filter(id = id).exists():
            product = models.Product.objects.filter(category=id,status=3)
            serializer = CategoryProductslistSerializer(product, many = True)
            return Response({'status': "200", 'message' : 'category products details','data' : {'category_products_data':serializer.data}})
        else:
            return Response({'status': "400", 'message' : 'requested data not found','data' : {}})

class random_products(APIView):
    def get(self,request,format = None):
        products = models.Product.objects.raw("select * from users_product order by rand() limit 10")
        serializer = All_ProductsListSerializer(products,many = True)
        return Response({'status': "200",'message' : 'all products list','data' : {'products_data':serializer.data}})

class product_view(APIView):
    def get(self, request, id, format = None):
        if models.Product.objects.filter(id = id).exists():
            product = models.Product.objects.filter(id = id)
            serializer = ProductViewSerializer(product, many = True)
            return Response({'status': "200", 'message' : 'product details','data' : {'product_view':serializer.data}})
        else:
            return Response({'status': "400", 'message' : 'requested data not found','data' : {}})
