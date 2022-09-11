from django.urls import path

import user_management.views as views


app_name = "user_management"

urlpatterns = [
    path('create_app_user/', views.AppUser.as_view(), name='create-app-user'),
    path('forget_password/', views.SendOtp.as_view(), name='forget-password'),
    path('verify_otp/', views.VerifyOtp.as_view(), name='verify-otp'),
    path('change_password/', views.ChangePassword.as_view(), name='change-password'),
    
]
