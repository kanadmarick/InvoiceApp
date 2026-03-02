from django.urls import path
from . import views

# Namespace for reverse URL lookups (e.g., 'businesses:business_list')
app_name = 'businesses'

# Business CRUD routes — all use UUID-based primary keys
urlpatterns = [
    path(
        '',
        views.BusinessListView.as_view(),
        name='business_list'),
    # List all user's businesses
    path('<uuid:pk>/', views.BusinessDetailView.as_view(),
         name='business_detail'),     # View single business
    path(
        'create/',
        views.BusinessCreateView.as_view(),
        name='business_create'),
    # Create new business
    path(
        '<uuid:pk>/update/',
        views.BusinessUpdateView.as_view(),
        name='business_update'),
    # Edit business
    path(
        '<uuid:pk>/delete/',
        views.BusinessDeleteView.as_view(),
        name='business_delete'),
    # Delete business
]
