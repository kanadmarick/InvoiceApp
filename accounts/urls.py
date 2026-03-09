from django.urls import path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from . import views

# Namespace for reverse URL lookups (e.g., 'accounts:login')
app_name = 'accounts'

urlpatterns = [
    # ── OpenAPI schema & Swagger UI ─────────────────────────────────────
    path('schema/', SpectacularJSONAPIView.as_view(urlconf='accounts.urls'), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='accounts:schema'), name='swagger-ui'),

    # ── API routes (JSON) ───────────────────────────────────────────────
    path('users/', views.AccountListAPIView.as_view(), name='account_list'),
    path('users/<uuid:pk>/', views.AccountDetailAPIView.as_view(), name='account_detail'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('guest-login/', views.GuestLoginAPIView.as_view(), name='guest_login'),
    path('register/', views.RegisterAPIView.as_view(), name='register'),
    path('logout/', views.LogoutAPIView.as_view(), name='logout'),
]
