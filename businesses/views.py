import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied

from .models import Business
from .serializers import BusinessSerializer, BusinessListSerializer

# Logger for the businesses app
logger = logging.getLogger(__name__)


# ── HTML Views (Template-based) ────────────────────────────────────────


class BusinessListView(LoginRequiredMixin, ListView):
    model = Business
    template_name = 'businesses/business_list.html'
    context_object_name = 'businesses'
    login_url = 'accounts:login'

    def get_queryset(self):
        return Business.objects.filter(owner=self.request.user)


class BusinessDetailView(LoginRequiredMixin, DetailView):
    model = Business
    template_name = 'businesses/business_detail.html'
    context_object_name = 'business'
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise DjangoPermissionDenied("You don't have permission to view this business.")
        return obj


class BusinessCreateView(LoginRequiredMixin, CreateView):
    model = Business
    template_name = 'businesses/business_form.html'
    fields = [
        'name',
        'email',
        'gstin',
        'logo',
        'brand_color',
        'address_line_1',
        'address_line_2',
        'city',
        'state',
        'pincode',
        'country']
    success_url = reverse_lazy('businesses:business_list')
    login_url = 'accounts:login'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        messages.success(self.request, 'Business created successfully!')
        return super().form_valid(form)


class BusinessUpdateView(LoginRequiredMixin, UpdateView):
    model = Business
    template_name = 'businesses/business_form.html'
    fields = [
        'name',
        'email',
        'gstin',
        'logo',
        'brand_color',
        'address_line_1',
        'address_line_2',
        'city',
        'state',
        'pincode',
        'country']
    success_url = reverse_lazy('businesses:business_list')
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise DjangoPermissionDenied("You don't have permission to edit this business.")
        return obj

    def form_valid(self, form):
        messages.success(self.request, 'Business updated successfully!')
        return super().form_valid(form)


class BusinessDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Business
    template_name = 'businesses/business_confirm_delete.html'
    success_url = reverse_lazy('businesses:business_list')
    login_url = 'accounts:login'

    def test_func(self):
        business = self.get_object()
        return business.owner == self.request.user

    def handle_no_permission(self):
        messages.error(self.request, "You don't have permission to delete this business.")
        return super().handle_no_permission()


# ── Business List + Create ──────────────────────────────────────────────


class BusinessListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /businesses/       — Lists all businesses owned by the logged-in user.
    POST /businesses/       — Creates a new business (owner is auto-assigned).
    Uses lightweight serializer for listings, full serializer for creation.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        # Use compact serializer for GET, full serializer for POST
        if self.request.method == 'POST':
            return BusinessSerializer
        return BusinessListSerializer

    def get_queryset(self):
        # Security: only show businesses owned by the current user
        return Business.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Auto-assign the current user as the business owner
        serializer.save(owner=self.request.user)
        logger.info(
            'User "%s" created business "%s"',
            self.request.user.username,
            serializer.instance.name,
        )


# ── Business Detail + Update + Delete ───────────────────────────────────


class BusinessDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /businesses/<uuid>/  — Retrieve a single business.
    PUT    /businesses/<uuid>/  — Full update of a business.
    PATCH  /businesses/<uuid>/  — Partial update of a business.
    DELETE /businesses/<uuid>/  — Delete a business.
    Only the business owner can access these endpoints.
    """
    serializer_class = BusinessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Security: scope queryset to the current user's businesses
        return Business.objects.filter(owner=self.request.user)

    def get_object(self):
        obj = super().get_object()
        # Double-check ownership (belt-and-suspenders with queryset filtering)
        if obj.owner != self.request.user:
            raise PermissionDenied(
                "You don't have permission to access this business.")
        return obj

    def perform_destroy(self, instance):
        logger.info(
            'User "%s" deleted business "%s"',
            self.request.user.username,
            instance.name,
        )
        instance.delete()
