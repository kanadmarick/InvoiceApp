from django.contrib import admin
from .models import Business


# Register Business model in the admin panel with custom display settings
@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    # Columns in the admin list view
    list_display = ('name', 'owner', 'gstin')
    # Enables search by name or GSTIN
    search_fields = ('name', 'gstin')

    # Load custom CSS to style the admin panel
    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }
