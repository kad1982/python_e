"""
URL configuration for online_store_clothing_rental project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from online_store_clothing_rental import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('homepage.urls', namespace='homepage')),
    path('admin/', admin.site.urls),
    path('users/', include('users.urls', namespace='users')),
    path('listing/', include('listing.urls', namespace='listing')),
    path('rental_request/', include('rental_request.urls', namespace='rental_request')),
    path('transaction/', include('transaction.urls', namespace='transaction')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)