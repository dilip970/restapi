from django.urls import path
from django.conf.urls import include, url
from .  import views

urlpatterns = [
    url(r'register/', views.Register.as_view() ),
    url(r'login/', views.Login, name="getToken"),
    url(r'uploadprofilepicture/', views.UploadProfilePicture, name="profilepicture"),
    url(r'checkapitoken/', views.Checktoken, name='checkapitoken'),
    url(r'doctorchangepassword/', views.doctor_changepassword.as_view()),
    url(r'doctorpatients/', views.doctor_patients.as_view()),
    url(r'timingsactive/', views.timings_active.as_view()),
    # url(r'timingsdeactive/', views.timings_deactive.as_view()),
    url(r'editprofiledetails/', views.edit_profiledetails.as_view()), 
    url(r'patientreviews/', views.patient_reviews.as_view()),  

    
]
