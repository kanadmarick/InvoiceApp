import os  # Access environment variables for guest credentials
import logging  # Log guest login events

from django.contrib import messages
from rest_framework import generics, permissions, status, serializers
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from accounts.models import CustomUser
from accounts.forms import CustomUserCreationForm
from accounts.serializers import (
    UserSerializer,
    UserListSerializer,
    RegisterSerializer,
    LoginSerializer,
)

# Logger for the accounts app — logs to security.log and general.log
logger = logging.getLogger(__name__)


# ── HTML Views (Template-based) ────────────────────────────────────────
# NOTE: These views are from the original template-based architecture.
# They are currently unused in the React-based SPA but kept for reference.


class AccountListView(ListView):
    model = CustomUser
    template_name = 'accounts/account_list.html'
    context_object_name = 'users'
    paginate_by = 9


class AccountDetailView(DetailView):
    model = CustomUser
    template_name = 'accounts/account_detail.html'
    context_object_name = 'user'


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('accounts:login')

    def post(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('accounts:login')


class GuestLoginView(View):
    def get(self, request):
        guest_username = os.getenv('GUEST_USERNAME')
        guest_password = os.getenv('GUEST_PASSWORD')

        if not guest_username or not guest_password:
            logger.warning(
                'Guest login attempted but GUEST_USERNAME/GUEST_PASSWORD not set in .env')
            messages.error(request, 'Guest login is not configured.')
            return redirect('accounts:login')

        user = authenticate(
            request,
            username=guest_username,
            password=guest_password)

        if user is not None:
            login(request, user)
            logger.info('Guest user "%s" logged in successfully', guest_username)
            messages.success(
                request,
                f'Welcome, {user.username}! You are logged in as a guest.')
            return redirect('home')

        logger.error(
            'Guest login failed for user "%s" — invalid credentials',
            guest_username)
        messages.error(request, 'Guest login failed. Please try a regular login.')
        return redirect('accounts:login')


class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Account created successfully! Please log in.')
        return response


# ── User Profile Endpoints ──────────────────────────────────────────────


class AccountListAPIView(generics.ListAPIView):
    """
    GET /accounts/
    Lists all user accounts. Restricted to admin/staff users.
    Returns a paginated list with lightweight user data.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAdminUser]


class AccountDetailAPIView(generics.RetrieveUpdateAPIView):
    """
    GET /accounts/<uuid>/      — Retrieve user profile
    PUT/PATCH /accounts/<uuid>/ — Update user profile
    Authenticated users can view/edit profiles.
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


# ── Authentication Endpoints ────────────────────────────────────────────


class RegisterAPIView(generics.CreateAPIView):
    """
    POST /accounts/register/
    Creates a new user account and returns JWT tokens for immediate login.
    Open to unauthenticated users (AllowAny).
    """
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Create the user via serializer (password is hashed by create_user)
        user = serializer.save()
        # Generate JWT token pair for the new user
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Account created successfully.',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
        }, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    """
    POST /accounts/login/
    Authenticates the user with username/password and returns JWT tokens.
    Also creates a session cookie for browsable API access.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = LoginSerializer  # For Swagger schema generation

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        # Create session (used by browsable API and Swagger UI)
        login(request, user)
        # Generate JWT token pair
        refresh = RefreshToken.for_user(user)
        logger.info('User "%s" logged in via API', user.username)
        return Response({
            'message': f'Welcome, {user.username}!',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
        })


class LogoutAPIView(APIView):
    """
    POST /accounts/logout/
    Logs out the user by terminating the session and blacklisting
    the refresh token (if provided in the request body).
    """
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=inline_serializer(
            name='LogoutRequestSerializer',
            fields={
                'refresh': serializers.CharField(required=False),
            },
        ),
        responses=inline_serializer(
            name='LogoutResponseSerializer',
            fields={
                'message': serializers.CharField(),
            },
        ),
    )
    def post(self, request):
        # Blacklist the refresh token to prevent reuse
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass  # Token may already be blacklisted or invalid
        # Destroy the server-side session
        logout(request)
        logger.info('User logged out via API')
        return Response(
            {'message': 'Logged out successfully.'},
            status=status.HTTP_200_OK,
        )


# ── Guest / Demo Login ──────────────────────────────────────────────────


class GuestLoginAPIView(APIView):
    """
    POST /accounts/guest-login/
    One-click demo login using credentials from environment variables.
    Allows portfolio visitors to explore the app without creating an account.
    Returns JWT tokens on success.
    """
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        request=None,
        responses={
            200: inline_serializer(
                name='GuestLoginSuccessSerializer',
                fields={
                    'message': serializers.CharField(),
                    'user': UserSerializer(),
                    'tokens': inline_serializer(
                        name='GuestLoginTokensSerializer',
                        fields={
                            'refresh': serializers.CharField(),
                            'access': serializers.CharField(),
                        },
                    ),
                },
            ),
            401: inline_serializer(
                name='GuestLoginUnauthorizedSerializer',
                fields={'error': serializers.CharField()},
            ),
            503: inline_serializer(
                name='GuestLoginUnavailableSerializer',
                fields={'error': serializers.CharField()},
            ),
        },
    )
    def post(self, request):
        # Read guest credentials from environment variables
        guest_username = os.getenv('GUEST_USERNAME')
        guest_password = os.getenv('GUEST_PASSWORD')

        # Guard: ensure guest credentials are configured in .env
        if not guest_username or not guest_password:
            logger.warning(
                'Guest login attempted but GUEST_USERNAME/GUEST_PASSWORD not set in .env')
            return Response(
                {'error': 'Guest login is not configured.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        # Authenticate the guest user against the database
        # NOTE: This assumes the guest user already exists.
        # In a real deployment, a management command or migration should ensure this user exists.
        user = authenticate(
            request=request,
            username=guest_username,
            password=guest_password,
        )

        if user is not None:
            # Create session for browsable API access
            login(request, user)
            logger.info('Guest user "%s" logged in successfully', guest_username)
            # Generate JWT token pair
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': f'Welcome, {user.username}! You are logged in as a guest.',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                },
            })
        else:
            # Auth failed — account may have been deleted or password changed
            logger.error(
                'Guest login failed for user "%s" — invalid credentials',
                guest_username)
            return Response(
                {'error': 'Guest login failed. Invalid credentials.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )
