from django.contrib import admin
from .models import Business

@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'gstin')
    search_fields = ('name', 'gstin')

    class Media:
        css = {
            'all': ('css/admin_custom.css',)
        }
    