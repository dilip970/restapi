  
from hashlib import new
from django.db.models import fields
from rest_framework import serializers
from users import models
from users.models import Doctor, Patient_Appoinments, Appoinment_Timings, Patient_Reviews

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

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Doctor
        fields  =   '__all__'

class DoctorRegisterSerializer(serializers.ModelSerializer):
    profile_picture = Base64ImageField(max_length=None, use_url=True)
    class Meta:
        model   =   Doctor
        fields  =    '__all__'

class DoctorProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Doctor
        fields  =   ['profile_picture']

class DoctorChangepasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Doctor
        fields  =   ['password']

class DoctorsPatientlist(serializers.ModelSerializer):
    class Meta:
        model   =   Patient_Appoinments
        fields  =   '__all__'

class TimingsActivateSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Appoinment_Timings
        fields  =   ['slot_time','slot_date']

class DoctorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Doctor
        fields  =   ['first_name','last_name','phone','address1','address2','city','state','profile_picture','pincode','bio']

class PatientReviewsSerializer(serializers.ModelSerializer):
    first_name  =   serializers.CharField(source    =   'patient.first_name')
    last_name   =   serializers.CharField(source    =   'patient.last_name')
    class Meta:
        model   =   Patient_Reviews
        fields  =   ['first_name','last_name','review_starts', 'review_text']