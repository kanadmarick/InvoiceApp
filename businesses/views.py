from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Business


# Lists all businesses owned by the current user
class BusinessListView(LoginRequiredMixin, ListView):
    model = Business
    template_name = 'businesses/business_list.html'
    context_object_name = 'businesses'
    login_url = 'accounts:login'

    def get_queryset(self):
        # Security: only show businesses owned by current user
        return Business.objects.filter(owner=self.request.user)


# Shows detailed info for a single business (with ownership check)
class BusinessDetailView(LoginRequiredMixin, DetailView):
    model = Business
    template_name = 'businesses/business_detail.html'
    context_object_name = 'business'
    login_url = 'accounts:login'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Security: only the owner can view this business
        if obj.owner != self.request.user:
            raise PermissionDenied(
                "You don't have permission to view this business.")
        return obj


# Form for creating a new business (auto-assigns current user as owner)
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
        # Automatically set current user as owner (not editable by user)
        form.instance.owner = self.request.user
        messages.success(self.request, "Business created successfully!")
        return super().form_valid(form)


# Form for editing a business (with ownership check)
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
        # Security: only the owner can edit this business
        if obj.owner != self.request.user:
            raise PermissionDenied(
                "You don't have permission to edit this business.")
        return obj

    def form_valid(self, form):
        messages.success(self.request, "Business updated successfully!")
        return super().form_valid(form)


# Confirmation page before deleting a business (uses UserPassesTestMixin)
class BusinessDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Business
    template_name = 'businesses/business_confirm_delete.html'
    success_url = reverse_lazy('businesses:business_list')
    login_url = 'accounts:login'

    def test_func(self):
        """Only allow business owner to delete"""
        business = self.get_object()
        return business.owner == self.request.user

    def handle_no_permission(self):
        """Show error message when permission is denied"""
        messages.error(
            self.request,
            "You don't have permission to delete this business.")
        return super().handle_no_permission()
