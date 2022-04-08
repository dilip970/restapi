from django.db import models
from django.db.models import fields
from rest_framework import serializers
from users.models import Pharmacy, Pharmacy_Reviews, Product,Categories

class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        from django.core.files.base import ContentFile
        import base64
        import six
        import uuid
        if isinstance(data, six.string_types):
            if 'data:' in data and ';base64,' in data:
                header, data = data.split(';base64,')
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')
            file_name = str(uuid.uuid4()).upper()[:12]
            file_extension = self.get_file_extension(file_name, decoded_file)
            complete_file_name = "%s.%s" % (file_name, file_extension, )
            data = ContentFile(decoded_file, name=complete_file_name)
        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr
        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension
        return extension

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Pharmacy
        fields  =   '__all__'

class PharmacyRegisterSerializer(serializers.ModelSerializer):
    pharmacy_image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model   =   Pharmacy
        fields  =   '__all__'

class PharmacyChangepasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Pharmacy
        fields  =   ['password']

class PharmacyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Pharmacy
        fields  =   '__all__'

class PharmacyProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Pharmacy
        fields  =   ['pharmacy_name', 'phone']

class PharmacyReviewsSerializer(serializers.ModelSerializer):
    first_name  =   serializers.CharField(source    =   'patient.first_name')
    last_name   =   serializers.CharField(source    =   'patient.last_name')
    class Meta:
        model   =   Pharmacy_Reviews
        fields  =   ['first_name','last_name','review_starts', 'review_text']

class AddProductSerializer(serializers.ModelSerializer):
    product_image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model   =   Product
        fields  =   '__all__'

class UpdateProductSerializer(serializers.ModelSerializer):
    product_image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model   =   Product
        fields  =   ['product_name','product_image','category','product_stock','product_price','description','discount','status']

class ProductSerializerStatus(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['status']

class AllCategoriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'

class All_ProductsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','product_name','product_code','product_image','product_price','description','discount','category','pharmacy']
        # fields = '__all__'

class CategoryProductslistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','product_name','product_code','product_image','product_price','description','discount','category','pharmacy']

class ProductViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','product_name','product_code','product_image','product_price','description','discount','category','pharmacy']
        