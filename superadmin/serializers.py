from django.db.models import fields
from rest_framework import serializers
from users.models import (Country, Patient, State, City, Pharmacy, SuperAdmin, Locations, Specializations,
 SubSpecializations, Doctor,Diagnostics, Tests, Categories,Product)


#Image to Base64 Conversion
#==========================
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


class AdminPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = ['password']

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = SuperAdmin
        fields = '__all__'

class PatientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'

class SpecializationsWiseDoctors(serializers.ModelSerializer):
    country_name    =   serializers.CharField(source    =   'country.country_name')
    state_name      =   serializers.CharField(source    =   'state.state_name')
    city_name       =   serializers.CharField(source    =   'city.city_name')
    specialization_name         =   serializers.CharField(source    =   'specialization.specialization')
    class Meta:
        model = Doctor
        fields = ('id','first_name', 'last_name', 'email', 'password', 'phone', 'address1', 'address2', 
        'pincode', 'bio','experience', 'consultation_fee', 'profile_picture', 'document', 'location_id',
        'status', 'specialization', 'specialization_name', 'country', 'state', 'city', 'country_name', 'state_name',
         'city_name')

class CountriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = "__all__"

class StatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = "__all__"
    def to_representation(self, instance):
        country_name  = super(StatesSerializer, self).to_representation(instance)
        country_name ['country'] = instance.country.country_name
        return country_name 

class CitiesSerializer(serializers.ModelSerializer):
    country_name    =   serializers.CharField(source    =   'country.country_name')
    state_name      =   serializers.CharField(source    =   'state.state_name')
    class Meta:
        model = City
        fields = ('id', 'city_name', 'country', 'country_name', 'state', 'state_name', 'status')
    
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Locations
        fields = '__all__'

class SpecializationsSerializerPOST(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model = Specializations
        fields = ('specialization', 'image')

class ActiveSpecializationsList(serializers.ModelSerializer):
    class Meta:
        model = Specializations
        fields = '__all__'

class SpecializationsSerializerGET(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model = Specializations
        fields = '__all__'

class SpecializationsSerializerStatus(serializers.ModelSerializer):
    class Meta:
        model = Specializations
        fields = ['status']

class SubSpecializationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSpecializations
        fields = '__all__'

class AddDoctorSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField(max_length=None, use_url=True)
    document = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model = Doctor
        fields = ('first_name', 'last_name', 'email', 'password','phone', 'address1', 'address2','city', 
        'state', 'country', 'pincode', 'bio', 'specialization','experience', 'consultation_fee', 
        'profile_picture', 'document')

class DoctorSerializer(serializers.ModelSerializer):
    country_name    =   serializers.CharField(source    =   'country.country_name')
    state_name      =   serializers.CharField(source    =   'state.state_name')
    city_name       =   serializers.CharField(source    =   'city.city_name')
    specialization_name         =   serializers.CharField(source    =   'specialization.specialization')
    class Meta:
        model = Doctor
        fields = ('id','first_name', 'last_name', 'email', 'password', 'phone', 'address1', 'address2', 
        'pincode', 'bio','experience', 'consultation_fee', 'profile_picture', 'document', 'location_id',
        'status', 'specialization', 'specialization_name', 'country', 'state', 'city', 'country_name', 'state_name',
         'city_name')


class UpdateDoctorSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField(max_length=None, use_url=True)
    document = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model = Doctor
        fields = ('first_name', 'last_name', 'email', 'phone', 'address1', 'address2', 'city', 
        'state', 'country', 'pincode', 'bio', 'specialization','experience', 'consultation_fee', 
        'profile_picture', 'document')


class DoctorStatusSerialize(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ['status']

class PharmacySerializer(serializers.ModelSerializer):
    class Meta:
        model = Pharmacy
        fields = '__all__'

class DiagnosticsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Diagnostics
        fields = '__all__'
        
class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tests
        fields = '__all__'


# Super Admin Pharmacy Category Serializers
#==========================================
class CategorySerializerGET(serializers.ModelSerializer):
    category_image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model = Categories
        fields = '__all__'


class CategorySerializerPOST(serializers.ModelSerializer):
    category_image = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model = Categories
        fields = ['category_name', 'category_image']


class CategorySerializerStatus(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ['status']

# Pharmacy Category
class AllCategoriesListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'


class PharmacyProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class ProductSerializerStatus(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['status']
