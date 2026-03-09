from django.urls import path
from drf_spectacular.views import SpectacularJSONAPIView, SpectacularSwaggerView
from . import views
from .pdf import InvoicePDFAPIView

# Namespace for reverse URL lookups (e.g., 'billings:invoice_list')
app_name = 'billings'

# Invoice CRUD routes — all use UUID-based primary keys in the URL
urlpatterns = [
    # ── OpenAPI schema & Swagger UI ─────────────────────────────────────
    path('schema/', SpectacularJSONAPIView.as_view(urlconf='billings.urls'), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='billings:schema'), name='swagger-ui'),

    # ── API routes (JSON) ───────────────────────────────────────────────
    path('', views.InvoiceListCreateAPIView.as_view(), name='billing_list'),
    path('invoices/', views.InvoiceListCreateAPIView.as_view(), name='invoice_list'),
    path('invoices/<uuid:pk>/', views.InvoiceDetailAPIView.as_view(), name='invoice_detail'),
    path('invoices/<uuid:pk>/pdf/', InvoicePDFAPIView.as_view(), name='invoice_pdf'),
]
