from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from .forms import InvoiceForm
from .models import Invoice

class InvoiceListView(ListView):
    model = Invoice
    template_name = 'billings/invoice_list.html'
    context_object_name = 'invoices'

class InvoiceDetailView(DetailView):
    model = Invoice
    template_name = 'billings/invoice_detail.html'
    context_object_name = 'invoice'

class InvoiceCreateView(CreateView):
    model = Invoice
    template_name = 'billings/invoice_form.html'
    form_class = InvoiceForm
    success_url = reverse_lazy('billings:invoice_list')

class InvoiceUpdateView(UpdateView):
    model = Invoice
    template_name = 'billings/invoice_form.html'
    form_class = InvoiceForm
    success_url = reverse_lazy('billings:invoice_list')

class InvoiceDeleteView(DeleteView):
    model = Invoice
    template_name = 'billings/invoice_confirm_delete.html'
    success_url = reverse_lazy('billings:invoice_list')
