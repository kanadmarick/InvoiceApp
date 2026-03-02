from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count, F
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from .forms import InvoiceForm
from .models import Invoice


# Displays paginated list of invoices with filtering by status, client,
# and search
class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'billings/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 10  # 10 invoices per page
    login_url = 'accounts:login'

    def get_queryset(self):
        # Security: only show invoices for businesses owned by current user
        user_businesses = self.request.user.businesses.all()
        queryset = Invoice.objects.filter(
            client__business__in=user_businesses).order_by('-created_at')

        # Filter by status — since status is a computed @property, we use
        # database-level annotation tricks to replicate the logic in SQL
        status = self.request.GET.get('status')
        if status:
            if status == 'DRAFT':
                # DRAFT = invoices with no milestones at all
                queryset = queryset.annotate(
                    milestone_count=Count('milestones')).filter(
                    milestone_count=0)
            elif status == 'PAID':
                # PAID = all milestones have status 'PAID'
                queryset = queryset.filter(
                    milestones__status='PAID').annotate(
                    paid_count=Count(
                        'milestones',
                        filter=Q(
                            milestones__status='PAID')),
                    total_count=Count('milestones')).filter(
                    paid_count=F('total_count'),
                    total_count__gt=0)
            elif status == 'OVERDUE':
                # OVERDUE = at least one milestone is overdue
                queryset = queryset.filter(
                    milestones__status='OVERDUE').distinct()
            elif status == 'PARTIALLY_PAID':
                # PARTIALLY_PAID = some milestones paid, but not all
                queryset = queryset.filter(
                    milestones__status='PAID').annotate(
                    paid_count=Count(
                        'milestones',
                        filter=Q(
                            milestones__status='PAID')),
                    total_count=Count('milestones')).exclude(
                    paid_count=F('total_count')).filter(
                        total_count__gt=0).distinct()
            elif status == 'PENDING':
                # PENDING = has milestones, but none are paid or overdue
                queryset = queryset.filter(
                    milestones__status='PENDING').exclude(
                    milestones__status__in=[
                        'PAID', 'OVERDUE']).distinct()

        # Filter by client name (partial, case-insensitive match)
        client = self.request.GET.get('client')
        if client:
            queryset = queryset.filter(client__name__icontains=client)

        # Search by invoice number or client name
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(client__name__icontains=search)
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        # Pass current filter values back to template for preserving form state
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['client_filter'] = self.request.GET.get('client', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


# Shows full invoice details (items, milestones, client info)
class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'billings/invoice_detail.html'
    context_object_name = 'invoice'
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Security: verify the invoice belongs to one of the current user's
        # businesses
        if obj.client.business.owner != self.request.user:
            raise PermissionDenied(
                "You don't have permission to view this invoice.")
        return obj

# Renders the invoice creation form with auto-generated invoice number


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    template_name = 'billings/invoice_form.html'
    form_class = InvoiceForm
    success_url = reverse_lazy('billings:invoice_list')
    login_url = 'accounts:login'

# Allows editing an existing invoice (with ownership check)


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    template_name = 'billings/invoice_form.html'
    form_class = InvoiceForm
    success_url = reverse_lazy('billings:invoice_list')
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Security: only the business owner can edit their invoices
        if obj.client.business.owner != self.request.user:
            raise PermissionDenied(
                "You don't have permission to edit this invoice.")
        return obj

# Confirmation page before deleting an invoice (with ownership check)


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'billings/invoice_confirm_delete.html'
    success_url = reverse_lazy('billings:invoice_list')
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.client.business.owner != self.request.user:
            raise PermissionDenied(
                "You don't have permission to delete this invoice.")
        return obj
