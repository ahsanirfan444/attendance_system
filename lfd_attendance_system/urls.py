
from django.contrib import admin
from django.urls import path,include
from user_management.views import CustomAuthLogin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-token-auth/', CustomAuthLogin.as_view(), name='api-token-auth/'),
    path('user_management/', include('user_management.urls')),
    path('attendance_api/', include('attendance_api.urls')),
    path('dashboard/', include('dashboard.urls')),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
