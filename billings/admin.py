from django.contrib import admin
from .models import Client, Invoice, InvoiceItem, Milestone, DraftItem

class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 1  # Shows one empty row by default

class MilestoneInline(admin.TabularInline):
    model = Milestone
    extra = 1

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'client', 'status', 'total_amount', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('invoice_number', 'client__name')
    inlines = [InvoiceItemInline, MilestoneInline]
    readonly_fields = ('id', 'created_at', 'updated_at') # Senior move: Protect the UUIDs
    list_display_links = ('invoice_number',)  # Make invoice number clickable to go to detail view
    actions = ['mark_as_paid'] # Custom action to mark selected invoices as paid

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'business', 'email')
    search_fields = ('name', 'email')
    list_filter = ('business',)

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('invoice', 'description', 'amount', 'due_date', 'status')
    list_filter = ('status', 'due_date')
    search_fields = ('description', 'invoice__invoice_number')

@admin.register(DraftItem)
class DraftItemAdmin(admin.ModelAdmin):
    list_display = ('business', 'description', 'unit_price')
    search_fields = ('description',)
    list_filter = ('business',)