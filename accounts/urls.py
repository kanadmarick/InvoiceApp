from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

# Namespace for reverse URL lookups (e.g., 'accounts:login')
app_name = 'accounts'

urlpatterns = [
    # User listing and authentication
    path('', views.AccountListView.as_view(), name='account_list'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path(
        'guest-login/',
        views.GuestLoginView.as_view(),
        name='guest_login'),
    # One-click demo login
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Password Reset Flow (4 steps):
    # Step 1: User enters email address
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='accounts/password_reset.html',
             email_template_name='accounts/password_reset_email.html',
             subject_template_name='accounts/password_reset_subject.txt',
             success_url='/accounts/password-reset/done/'
         ),
         name='password_reset'),
    # Step 2: Confirmation that email was sent
    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='accounts/password_reset_done.html'
         ),
         name='password_reset_done'),
    # Step 3: User clicks link in email, enters new password
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/password_reset_confirm.html',
             success_url='/accounts/password-reset-complete/'
         ),
         name='password_reset_confirm'),
    # Step 4: Success page, password has been changed
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # User profile (UUID-based URL)
    path(
        '<uuid:pk>/',
        views.AccountDetailView.as_view(),
        name='account_detail'),
]
