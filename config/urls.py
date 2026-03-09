"""
URL configuration for invoices project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from . import views

# Root URL routing — delegates to each app's own urls.py
urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),
    # API landing page
    path('', SpectacularSwaggerView.as_view(url_name='schema'), name='home'),
    # Global OpenAPI schema and Swagger UI
    path('api/schema/', SpectacularJSONAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    # Dashboard API endpoint (JSON)
    path('api/dashboard/', views.DashboardAPIView.as_view(), name='dashboard-api'),
    path(
        'accounts/',
        include(
            'accounts.urls',
            namespace='accounts')),
    # Auth & user profiles
    path(
        'businesses/',
        include(
            'businesses.urls',
            namespace='businesses')),
    # Business CRUD
    path(
        'billings/',
        include(
            'billings.urls',
            namespace='billings')),
    # Invoice management
]

# Serve user-uploaded media files during development (nginx/S3 handles
# this in production)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
