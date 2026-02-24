from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.AccountListView.as_view(), name='account_list'),
    path('<int:pk>/', views.AccountDetailView.as_view(), name='account_detail'),
]
