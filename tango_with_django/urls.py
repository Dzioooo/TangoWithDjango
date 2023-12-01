from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

from rango import views

urlpatterns = [
    path('', RedirectView.as_view(url='/rango/', permanent=True)),
    path('rango/', include('rango.urls')),
    path('admin/', admin.site.urls),
    path('accounts/register/', views.MyRegistrationView.as_view(),
         name='registration_register'),
    path('accounts/login/', views.UserLoginView.as_view(), 
         name='custom_login'),
    path('accounts/', include('registration.backends.simple.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
