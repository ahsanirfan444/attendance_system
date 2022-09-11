from django.urls import path

import dashboard.views as views


app_name = "dashboard"

urlpatterns = [
    path('add_shift/', views.CreateShiftAPI.as_view(), name='add-shift'),
    path('user_list/', views.UsersListAPI.as_view(), name='user-list'),
    path('shift_list/', views.ShiftListAPI.as_view(), name='shift-list'),
]
