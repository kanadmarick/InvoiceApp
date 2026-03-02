from django.contrib import admin
from .models import Client, Invoice, InvoiceItem, Milestone, DraftItem

# Inline editors — shown inside the Invoice admin page for related objects


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1  # Shows one empty row by default for quick entry


class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1  # Shows one empty row by default


# Main invoice admin with inline items and milestones
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = (
        'invoice_number',
        'client',
        'status',
        'total_amount',
        'created_at')  # Table columns
    # Sidebar date filter
    list_filter = ('created_at',)
    # Search by invoice # or client
    search_fields = ('invoice_number', 'client__name')
    # Edit items/milestones on same page
    inlines = [InvoiceItemInline, MilestoneInline]
    # Protect UUID and timestamps
    readonly_fields = ('id', 'created_at', 'updated_at')
    # Clickable link to detail
    list_display_links = ('invoice_number',)
    # Custom bulk action (TODO: implement)
    actions = ['mark_as_paid']


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'email')               # Table columns
    # Searchable fields
    search_fields = ('name', 'email')
    # Filter by business
    list_filter = ('business',)


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'amount', 'due_date', 'status')
    # Filter by payment status or due date
    list_filter = ('status', 'due_date')
    search_fields = ('description', 'invoice__invoice_number')


# Reusable line items that businesses save as templates
@admin.register(DraftItem)
class DraftItemAdmin(admin.ModelAdmin):
    list_display = ('business', 'description', 'unit_price')
    search_fields = ('description',)
    list_filter = ('business',)
