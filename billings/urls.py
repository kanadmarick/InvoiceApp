from django.urls import path
from . import views

# Namespace for reverse URL lookups (e.g., 'billings:invoice_list')
app_name = 'billings'

# Invoice CRUD routes — all use UUID-based primary keys in the URL
urlpatterns = [
    path(
        '',
        views.InvoiceListView.as_view(),
        name='billing_list'),
    # /billings/ → invoice list
    # /billings/invoices/ → same list (canonical URL)
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/create/', views.InvoiceCreateView.as_view(),
         name='invoice_create'),  # /billings/invoices/create/
    path(
        'invoices/<uuid:pk>/',
        views.InvoiceDetailView.as_view(),
        name='invoice_detail'),
    # Single invoice view
    path(
        'invoices/<uuid:pk>/update/',
        views.InvoiceUpdateView.as_view(),
        name='invoice_update'),
    # Edit invoice
    path(
        'invoices/<uuid:pk>/delete/',
        views.InvoiceDeleteView.as_view(),
        name='invoice_delete'),
    # Delete invoice
]
