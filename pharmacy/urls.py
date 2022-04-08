from django.urls import path
from django.conf.urls import include, url
from .  import views

urlpatterns = [
    url(r'register/', views.Register.as_view()),
    url(r'login/', views.Login),
    url(r'changepassword/', views.change_password.as_view()),
    url(r'profileupdate/',views.profile_update.as_view()), 
    url(r'pharmacyreviews/', views.pharmacy_reviews.as_view()),

    url(r'addproduct/', views.Add_Product.as_view()), 
    url(r'editproduct/(?P<id>\d+)/', views.Edit_Product.as_view()), 
    url(r'productstatus/(?P<id>\d+)/', views.Product_Status.as_view()),
    
    url(r'allcategories/', views.All_Categories.as_view()), 
    url(r'randomproducts/',views.random_products.as_view()), # it display random products  
    url(r'categoryproductslist/(?P<id>\d+)/',views.category_productslist.as_view()),
    url(r'productview/(?P<id>\d+)/', views.product_view.as_view()),

]