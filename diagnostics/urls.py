from django.urls import path
from django.conf.urls import include, url
from .  import views

urlpatterns = [
    url(r'register/', views.Register.as_view()),
    url(r'login/', views.Login, name="getToken"),
    url(r'changepassword/', views.change_password.as_view()),
    url(r'profileupdate/',views.profile_update.as_view()), 
    url(r'diagnosticsreviews/', views.diagnostics_reviews.as_view()), 
    url(r'addtests/',views.add_tests.as_view()),
    url(r'edittest/(?P<id>\d+)/', views.edit_test.as_view()),
    url(r'teststatus/(?P<id>\d+)/',views.test_status.as_view()),   

]