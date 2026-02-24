from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Business

class BusinessListView(ListView):
    model = Business
    template_name = 'businesses/business_list.html'
    context_object_name = 'businesses'

class BusinessDetailView(DetailView):
    model = Business
    template_name = 'businesses/business_detail.html'
    context_object_name = 'business'

class BusinessCreateView(CreateView):
    model = Business
    template_name = 'businesses/business_form.html'
    fields = ['name', 'owner', 'email', 'gstin', 'logo', 'brand_color', 
              'address_line_1', 'address_line_2', 'city', 'state', 'pincode', 'country']
    success_url = reverse_lazy('businesses:business_list')

class BusinessUpdateView(UpdateView):
    model = Business
    template_name = 'businesses/business_form.html'
    fields = ['name', 'owner', 'email', 'gstin', 'logo', 'brand_color',
              'address_line_1', 'address_line_2', 'city', 'state', 'pincode', 'country']
    success_url = reverse_lazy('businesses:business_list')

class BusinessDeleteView(UserPassesTestMixin, DeleteView):
    model = Business
    template_name = 'businesses/business_confirm_delete.html'
    success_url = reverse_lazy('businesses:business_list')
    
    def test_func(self):
        """Only allow business owner or superuser to delete"""
        business = self.get_object()
        user = self.request.user
        return user.is_superuser or business.owner == user
    
    def handle_no_permission(self):
        """Add error message when permission denied"""
        messages.error(self.request, "You don't have permission to delete this business. Only the business owner or superuser can delete it.")
        return super().handle_no_permission()
