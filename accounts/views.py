import os  # Access environment variables for guest credentials
import logging  # Log guest login events
from django.views.generic import ListView, DetailView
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.views import View
from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm

# Logger for the accounts app — logs to security.log and general.log
logger = logging.getLogger(__name__)


# Lists all user accounts (admin/staff use)
class AccountListView(ListView):
    model = CustomUser
    template_name = 'accounts/account_list.html'
    context_object_name = 'users'
    paginate_by = 9  # Show 9 users per page (3x3 grid)


# Shows a single user's profile details
class AccountDetailView(DetailView):
    model = CustomUser
    template_name = 'accounts/account_detail.html'
    context_object_name = 'user'


# Handles user login with error messages on failure
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True  # Skip login page if already logged in

    def get_success_url(self):
        return reverse_lazy('home')  # Go to dashboard after login

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


# Handles logout via both GET and POST requests (for link and form-based
# logout)
class CustomLogoutView(View):
    """Handle both GET and POST logout requests"""

    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('accounts:login')

    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('accounts:login')


# One-click guest/demo login — authenticates using credentials from .env
# Allows portfolio visitors to explore the app without creating an account
class GuestLoginView(View):
    def get(self, request):
        # Read guest credentials from environment variables
        guest_username = os.getenv('GUEST_USERNAME')
        guest_password = os.getenv('GUEST_PASSWORD')

        # Guard: ensure guest credentials are configured
        if not guest_username or not guest_password:
            logger.warning(
                'Guest login attempted but GUEST_USERNAME/GUEST_PASSWORD not set in .env')
            messages.error(request, 'Guest login is not configured.')
            return redirect('accounts:login')

        # Authenticate the guest user against the database
        user = authenticate(
            request,
            username=guest_username,
            password=guest_password)

        if user is not None:
            login(request, user)  # Create session for the guest user
            logger.info(
                'Guest user "%s" logged in successfully',
                guest_username)
            messages.success(
                request, f'Welcome, {
                    user.username}! You are logged in as a guest.')
            return redirect('home')  # Send to dashboard
        else:
            # Auth failed — account may have been deleted or password changed
            logger.error(
                'Guest login failed for user "%s" — invalid credentials',
                guest_username)
            messages.error(
                request, 'Guest login failed. Please try a regular login.')
            return redirect('accounts:login')


# Handles new user registration with custom form
class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    # Redirect to login after registration
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            'Account created successfully! Please log in.')
        return response
