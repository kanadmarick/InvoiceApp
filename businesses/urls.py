from django.urls import path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from . import views

# Namespace for reverse URL lookups (e.g., 'businesses:business_list')
app_name = 'businesses'

# Business CRUD routes — all use UUID-based primary keys
urlpatterns = [
    # ── OpenAPI schema & Swagger UI ─────────────────────────────────────
    path('schema/', SpectacularJSONAPIView.as_view(urlconf='businesses.urls'), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='businesses:schema'), name='swagger-ui'),

    # ── API routes (JSON) ───────────────────────────────────────────────
    path('', views.BusinessListCreateAPIView.as_view(), name='business_list'),
    path('<uuid:pk>/', views.BusinessDetailAPIView.as_view(), name='business_detail'),
]
