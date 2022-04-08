from django.urls import path
from django.conf.urls import include, url
from .  import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    #Pillbro Patient URL's
    # =====================

    url(r'register/', views.Register.as_view() ),
    url(r'login/', views.Login, name="login"),
    # url(r'upload/profilepicture', views.UploadProfilePicture, name="profilepicture"),
    # url(r'checkapitoken/', views.Checktoken, name='checkapitoken')
    url(r'patientchangepassword/',views.patient_change_password.as_view()), 
    url(r'patientprofileupdate/', views.patientprofile_update.as_view()),
    url(r'patientappointment/', views.patient_appointment.as_view()),
    url(r'patientlabappointment/',views.patient_lab_appointment.as_view()),
    url(r'patientorder/',views.patient_order.as_view()),
    url(r'deleteorder/(?P<id>\d+)/', csrf_exempt(views.delete_order), name="delete_order"),
    url(r'patientordertest/',views.patientorder_test.as_view()),
    url(r'deletetest/(?P<id>\d+)/',csrf_exempt(views.delete_test)),
    url(r'patientticket/', views.patient_ticket.as_view()),
    url(r'patientdiagnosticscart/', views.patient_diagnostics_cart.as_view()),
    url(r'patientpharmacycart/', views.patient_pharmacy_cart.as_view())
]
