import logging

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from django.db.models import Q, Count, F
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import InvoiceForm
from .models import Invoice
from .serializers import (
    InvoiceSerializer,
    InvoiceListSerializer,
    InvoiceCreateUpdateSerializer,
)

# Logger for the billings app
logger = logging.getLogger(__name__)


# ── HTML Views (Template-based) ────────────────────────────────────────


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = 'billings/invoice_list.html'
    context_object_name = 'invoices'
    paginate_by = 10
    login_url = 'accounts:login'

    def get_queryset(self):
        user_businesses = self.request.user.businesses.all()
        queryset = Invoice.objects.filter(
            client__business__in=user_businesses).order_by('-created_at')

        status_param = self.request.GET.get('status')
        if status_param:
            if status_param == 'DRAFT':
                queryset = queryset.annotate(
                    milestone_count=Count('milestones')).filter(
                    milestone_count=0)
            elif status_param == 'PAID':
                queryset = queryset.filter(
                    milestones__status='PAID').annotate(
                    paid_count=Count(
                        'milestones',
                        filter=Q(
                            milestones__status='PAID')),
                    total_count=Count('milestones')).filter(
                    paid_count=F('total_count'),
                    total_count__gt=0)
            elif status_param == 'OVERDUE':
                queryset = queryset.filter(
                    milestones__status='OVERDUE').distinct()
            elif status_param == 'PARTIALLY_PAID':
                queryset = queryset.filter(
                    milestones__status='PAID').annotate(
                    paid_count=Count(
                        'milestones',
                        filter=Q(
                            milestones__status='PAID')),
                    total_count=Count('milestones')).exclude(
                    paid_count=F('total_count')).filter(
                        total_count__gt=0).distinct()
            elif status_param == 'PENDING':
                queryset = queryset.filter(
                    milestones__status='PENDING').exclude(
                    milestones__status__in=[
                        'PAID', 'OVERDUE']).distinct()

        client = self.request.GET.get('client')
        if client:
            queryset = queryset.filter(client__name__icontains=client)

        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search) |
                Q(client__name__icontains=search)
            )

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['client_filter'] = self.request.GET.get('client', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'billings/invoice_detail.html'
    context_object_name = 'invoice'
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.client.business.owner != self.request.user:
            raise DjangoPermissionDenied(
                "You don't have permission to view this invoice.")
        return obj


class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    template_name = 'billings/invoice_form.html'
    form_class = InvoiceForm
    success_url = reverse_lazy('billings:invoice_list')
    login_url = 'accounts:login'


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    template_name = 'billings/invoice_form.html'
    form_class = InvoiceForm
    success_url = reverse_lazy('billings:invoice_list')
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.client.business.owner != self.request.user:
            raise DjangoPermissionDenied(
                "You don't have permission to edit this invoice.")
        return obj


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = 'billings/invoice_confirm_delete.html'
    success_url = reverse_lazy('billings:invoice_list')
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.client.business.owner != self.request.user:
            raise DjangoPermissionDenied(
                "You don't have permission to delete this invoice.")
        return obj


# ── Invoice List + Create ───────────────────────────────────────────────


class InvoiceListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /billings/invoices/        — Paginated list with filtering.
    POST /billings/invoices/        — Create a new invoice with inline client data.

    Supports query parameters:
      ?status=DRAFT|PAID|OVERDUE|PARTIALLY_PAID|PENDING
      ?client=<name>        — partial, case-insensitive client name match
      ?search=<term>        — searches invoice number or client name
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # Use compact serializer for GET, create/update serializer for POST
        if self.request.method == 'POST':
            return InvoiceCreateUpdateSerializer
        return InvoiceListSerializer

    def get_queryset(self):
        # Security: only show invoices for the current user's businesses
        user_businesses = self.request.user.businesses.all()
        queryset = Invoice.objects.filter(
            client__business__in=user_businesses,
        ).select_related(
            'client', 'client__business',
        ).prefetch_related(
            'items', 'milestones',
        ).order_by('-created_at')

        # ── Status filter ───────────────────────────────────────────────
        # Status is a computed @property, so we replicate the logic in SQL
        status_param = self.request.query_params.get('status')
        if status_param:
            if status_param == 'DRAFT':
                # DRAFT = invoices with no milestones at all
                queryset = queryset.annotate(
                    milestone_count=Count('milestones'),
                ).filter(milestone_count=0)

            elif status_param == 'PAID':
                # PAID = all milestones have status 'PAID'
                queryset = queryset.filter(
                    milestones__status='PAID',
                ).annotate(
                    paid_count=Count(
                        'milestones', filter=Q(milestones__status='PAID')),
                    total_count=Count('milestones'),
                ).filter(paid_count=F('total_count'), total_count__gt=0)

            elif status_param == 'OVERDUE':
                # OVERDUE = at least one milestone is overdue
                queryset = queryset.filter(
                    milestones__status='OVERDUE',
                ).distinct()

            elif status_param == 'PARTIALLY_PAID':
                # PARTIALLY_PAID = some milestones paid, but not all
                queryset = queryset.filter(
                    milestones__status='PAID',
                ).annotate(
                    paid_count=Count(
                        'milestones', filter=Q(milestones__status='PAID')),
                    total_count=Count('milestones'),
                ).exclude(
                    paid_count=F('total_count'),
                ).filter(total_count__gt=0).distinct()

            elif status_param == 'PENDING':
                # PENDING = has milestones, but none are paid or overdue
                queryset = queryset.filter(
                    milestones__status='PENDING',
                ).exclude(
                    milestones__status__in=['PAID', 'OVERDUE'],
                ).distinct()

        # ── Client name filter ──────────────────────────────────────────
        client = self.request.query_params.get('client')
        if client:
            queryset = queryset.filter(client__name__icontains=client)

        # ── Full-text search (invoice number or client name) ────────────
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(invoice_number__icontains=search)
                | Q(client__name__icontains=search),
            )

        return queryset.distinct()


# ── Invoice Detail + Update + Delete ────────────────────────────────────


class InvoiceDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /billings/invoices/<uuid>/  — Full invoice with nested items & milestones.
    PUT    /billings/invoices/<uuid>/  — Full update of invoice + client + items.
    PATCH  /billings/invoices/<uuid>/  — Partial update.
    DELETE /billings/invoices/<uuid>/  — Delete invoice.
    Only the business owner can access their invoices.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # Use the writable serializer for PUT/PATCH, read-only for GET
        if self.request.method in ('PUT', 'PATCH'):
            return InvoiceCreateUpdateSerializer
        return InvoiceSerializer

    def get_queryset(self):
        # Security: scope to the current user's businesses
        user_businesses = self.request.user.businesses.all()
        return Invoice.objects.filter(
            client__business__in=user_businesses,
        ).select_related(
            'client', 'client__business',
        ).prefetch_related('items', 'milestones')

    def get_object(self):
        obj = super().get_object()
        # Double-check ownership
        if obj.client.business.owner != self.request.user:
            raise PermissionDenied(
                "You don't have permission to access this invoice.")
        return obj

    def perform_destroy(self, instance):
        logger.info(
            'User "%s" deleted invoice "%s"',
            self.request.user.username,
            instance.invoice_number,
        )
        instance.delete()
