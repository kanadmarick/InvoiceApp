
from django.urls import path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView

app_name = 'core'  # Namespace reserved for future core-level routes

# No routes yet — core provides models and template tags, not views
urlpatterns = [
	# Core app OpenAPI schema and Swagger UI
	path('schema/', SpectacularJSONAPIView.as_view(urlconf='core.urls'), name='schema'),
	path('docs/', SpectacularSwaggerView.as_view(url_name='core:schema'), name='swagger-ui'),
]
