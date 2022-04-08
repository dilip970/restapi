from hashlib import new
import pharmacy
from django.db.models import fields
from rest_framework import serializers
from users import models
from users.models import Diagnostics, Diagnostics_Reviews,Tests

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



class DiagnosticsRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Diagnostics
        fields  =   ['diagnostic_name', 'first_name', 'last_name', 'phone', 'email', 'password']

class DiagnosticsChangepasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Diagnostics
        fields  =   ['password']

class DiagnosticsProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Diagnostics
        fields  =   '__all__'

class DiagnosticsProfileEditSerializer(serializers.ModelSerializer):
    class Meta:
        model   =   Diagnostics
        fields  =   ['diagnostic_name', 'phone']

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tests
        fields = '__all__'

class DiagnosticsReviewsSerializer(serializers.ModelSerializer):
    first_name  =   serializers.CharField(source    =   'patient.first_name')
    last_name   =   serializers.CharField(source    =   'patient.last_name')
    class Meta:
        model   =   Diagnostics_Reviews
        fields  =   ['first_name','last_name','review_starts', 'review_text']