from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bakery.urls')),  # Asegúrate de que 'bakery' es el nombre de tu aplicación
]