import re

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from accounts.models import CustomUser


# ── User Profile Serializers ────────────────────────────────────────────


class UserSerializer(serializers.ModelSerializer):
    """Full user profile serializer for detail and update views."""

    # Expose the @property defined on CustomUser
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'full_name', 'phone_number', 'bio', 'profile_image',
            'is_premium', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'username', 'is_premium', 'created_at', 'updated_at']


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for paginated user listings."""

    full_name = serializers.ReadOnlyField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'profile_image', 'is_premium']


# ── Authentication Serializers ──────────────────────────────────────────


class RegisterSerializer(serializers.ModelSerializer):
    """
    Handles new user registration with password confirmation.
    Returns the created user; the view generates JWT tokens.
    """

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        write_only=True,
        label='Confirm password',
        style={'input_type': 'password'},
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, data):
        """Ensure both passwords match."""
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {'password2': 'Passwords do not match.'})
        return data

    def create(self, validated_data):
        """Create user with hashed password (create_user handles hashing)."""
        validated_data.pop('password2')
        return CustomUser.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validates username/password credentials and returns the authenticated user."""

    username = serializers.CharField()
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
    )

    def validate(self, data):
        """Authenticate against the database; attach user to validated_data."""
        user = authenticate(
            username=data['username'],
            password=data['password'],
        )
        if not user:
            raise serializers.ValidationError('Invalid username or password.')
        if not user.is_active:
            raise serializers.ValidationError('This account is inactive.')
        data['user'] = user
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    """Accepts an email address to initiate password reset."""

    email = serializers.EmailField()

    def validate_email(self, value):
        """Normalize the email; existence check happens in the view."""
        return value.lower().strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Accepts new password after clicking the reset link."""

    new_password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'},
    )
    new_password2 = serializers.CharField(
        write_only=True,
        label='Confirm new password',
        style={'input_type': 'password'},
    )

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError(
                {'new_password2': 'Passwords do not match.'})
        return data
