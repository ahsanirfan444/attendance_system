from django.urls import path

import attendance_api.views as views


app_name = "attendance_api"

urlpatterns = [
    path('punch/', views.PunchAPI.as_view(), name='punch'),
    path('user_status/', views.UserStatus.as_view(), name='user-status'),
    path('add_client/', views.ClientAPI.as_view(), name='user-status'),
    path('client_list/', views.ClientAPI.as_view(), name='user-status'),
    path('attendance_record/', views.AttendanceRecordAPI.as_view(), name='attendance-record'),
    
]
