  
from django.db import models
from django.db.models import fields
from rest_framework import serializers
from users.models import Patient, Patient_Appoinments, Patient_Lab_Appointments, Patient_Orders, Patient_Tickets, Patient_Cart

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

class PatientRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name' ,'phone', 'email', 'password']

class PatientProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['first_name','last_name', 'email', 'gender', 'dob', 'bloodgroup', 'houseno', 'street', 'city','state', 'country', 'pincode', 'phone', 'language']

class PatientLabAppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient_Lab_Appointments
        fields = ['patient', 'patient_name', 'phone','email','gender','age','medical_problem','test_price','doctor_name', 'test_total','test_name', 'test_status', 'lab_name']


class PatientConsultSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient_Appoinments
        fields = ['patient_name', "appointment_id",'' 'medical_problem','doctor_name','clinic_name']

class PatientOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient_Orders
        fields = ['product_name', 'quantity', 'product_price', 'order_total', 'order_status',
        'patient'] 

class PatientTestOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient_Lab_Appointments
        fields = ['patient','patient_name','test_name','lab_name','test_price','test_total']
        
class PatientTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient_Tickets
        fields = ['patient','title','description','ticket_status']

class PatientCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient_Cart
        # fields = ['patient', 'product_name', 'product_price', 'product_qty', 'total_price', 'test_name', 'test_price']
        fields = '__all__'

class PatientPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['password']

class UsersRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = '__all__'