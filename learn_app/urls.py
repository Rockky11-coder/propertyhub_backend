from django.urls import path
from .import views


urlpatterns = [
   
     path('api/signup/', views.SignupAPI.as_view(),name='signupapi'),
     path('api/login/', views.LoginAPI.as_view(),name='loginapi'),
     path('api/forgetpw/',views.ForgetpwAPI.as_view(),name='forgetpwapi')
]