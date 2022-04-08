from django.conf.urls import url
from .  import views

urlpatterns = [
    url(r'login/', views.Login, name="login"),
    url(r'register/', views.Register, name="register"),
    url(r'checktoken/', views.Checktoken, name="checktoken"),
    url(r'changepassword/', views.Change_Password.as_view()),


    #Location URL's
    url(r'countries/', views.Countries.as_view()), 
    url(r'states/(?P<id>\d+)/', views.States.as_view()), 
    url(r'cities/(?P<id>\d+)/', views.Cities.as_view()),

    url(r'totalcountries/', views.Total_Countries.as_view()),  
    url(r'totalstates/', views.Total_States.as_view()),  
    url(r'totalcities/', views.Total_Cities.as_view()),


    #Pharmacy Category Add & Edit & Status
    url(r'addcategory/', views.add_category.as_view()), 
    url(r'editcategory/(?P<id>\d+)/', views.edit_category.as_view()),
    url(r'categorystatus/(?P<id>\d+)/', views.category_status.as_view()),
    url(r'allcategories/', views.All_Categories.as_view()),
    url(r'pharmacyproductslist/(?P<id>\d+)/',views.pharmacy_productslist.as_view()),
    url(r'productstatus/(?P<id>\d+)/', views.Product_Status.as_view()),

    #dashboard
    url(r'dashboardcount/',views.dashboardcount.as_view()),

    
    #Patient
    url(r'patientlist/', views.Patient_List.as_view()), 

    #Adding Super Admin URL's
    url(r'addlocations/', views.add_locations.as_view()),
    url(r'addspecializations/', views.add_specializations.as_view()),
    url(r'activespecializations/', views.Active_Specializations.as_view()),
    
    url(r'addsubspecializations/', views.add_subspecializations.as_view()),
    url(r'adddoctors/', views.add_doctors.as_view()),
    url(r'addpharmacy/',views.add_pharmacy.as_view()),
    url(r'adddiagnostics/',views.add_diagnostics.as_view()),
    
    #Edit Super Admin URL's
    url(r'editspecializations/(?P<id>\d+)/', views.edit_specializations.as_view()),
    url(r'editsubspecializations/(?P<id>\d+)/', views.edit_subspecializations.as_view()),
    url(r'editdoctor/(?P<id>\d+)/', views.edit_doctor.as_view()),
    url(r'editpharmacy/(?P<id>\d+)/', views.edit_pharmacy.as_view()),
    url(r'editdiagnostics/(?P<id>\d+)/', views.edit_diagnostics.as_view()),
    url(r'editlocation/(?P<id>\d+)/',views.edit_location.as_view()),

    #Active and Inactive URL's for Superadmin
    url(r'locationstatus/(?P<id>\d+)/', views.location_status.as_view()),
    url(r'specializationsstatus/(?P<id>\d+)/', views.specializations_status.as_view()),
    url(r'subspecializationstatus/(?P<id>\d+)/', views.subspecialization_status.as_view()),
    url(r'pharmacystatus/(?P<id>\d+)/', views.pharmacy_status.as_view()),
    url(r'doctorstatus/(?P<id>\d+)/', views.doctor_status.as_view()),
    url(r'diagnosticsstatus/(?P<id>\d+)/',views.diagnostics_status.as_view()),

    #for website
    url(r'doctordetails/',views.doctor_details.as_view()),
    url(r'doctoriddetails/(?P<id>\d+)/',views.doctor_id_details.as_view()),
    url(r'medicinedetails/',views.medicine_details.as_view()),
    url(r'medicineiddetails/(?P<id>\d+)/',views.medicine_id_details.as_view()),
    url(r'testdetails/',views.test_details.as_view()),
    url(r'testiddetails/(?P<id>\d+)/',views.test_id_details.as_view()),
    url(r'diagnosticsdetails/',views.diagnostics_details.as_view()),
    url(r'diagnosticsiddetails/(?P<id>\d+)/',views.diagnostics_id_details.as_view()),
    url(r'specializationdoctors/(?P<id>\d+)/',views.specialization_doctors.as_view()), 

       
]

