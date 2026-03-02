from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


# Register CustomUser with the admin panel, extending Django's built-in
# UserAdmin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Columns shown in the user list table
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone_number',
        'is_premium',
        'is_staff')
    # Sidebar filters for quick filtering
    list_filter = ('is_premium', 'is_staff', 'is_active', 'created_at')
    # Fields searchable from the admin search bar
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
        'phone_number')
    # These fields are display-only (can't be edited)
    readonly_fields = ('id', 'created_at', 'updated_at')

    # Organize the edit form into collapsible sections
    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'bio', 'profile_image')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_premium', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'last_login', 'date_joined'), 'classes': ('collapse',)}),
    )
