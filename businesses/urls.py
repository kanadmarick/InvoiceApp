from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('', views.BusinessListView.as_view(), name='business_list'),
    path('<uuid:pk>/', views.BusinessDetailView.as_view(), name='business_detail'),
    path('create/', views.BusinessCreateView.as_view(), name='business_create'),
    path('<uuid:pk>/update/', views.BusinessUpdateView.as_view(), name='business_update'),
    path('<uuid:pk>/delete/', views.BusinessDeleteView.as_view(), name='business_delete'),
]
