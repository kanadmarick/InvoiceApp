import re

from django import forms

from businesses.models import Business
from .models import Client, Invoice


# Custom form that creates/updates both Invoice and Client in a single form.
# Combines invoice fields with inline client & address fields.
class InvoiceForm(forms.ModelForm):
    # Business selector — determines which business this invoice is billed from
    business = forms.ModelChoiceField(
        queryset=Business.objects.all(),
        required=True,
        label="Business",
        empty_label="Select a business",
    )
    # Client info fields (stored in the Client model, not Invoice)
    client_name = forms.CharField(max_length=255, label="Client Name")
    client_email = forms.EmailField(label="Client Email")
    # Address fields (from ContactInfoModel mixin on Client)
    address_line_1 = forms.CharField(max_length=255, label="Address Line 1")
    address_line_2 = forms.CharField(
        max_length=255, required=False, label="Address Line 2"
    )
    city = forms.CharField(max_length=100, label="City")
    state = forms.CharField(max_length=100, label="State")
    pincode = forms.CharField(max_length=10, label="Pincode")
    country = forms.CharField(max_length=100, label="Country", initial="India")

    class Meta:
        model = Invoice
        # Only these fields live on Invoice itself
        fields = ["invoice_number", "notes"]

    @staticmethod
    def _next_invoice_number():
        """Auto-generates the next invoice number (e.g., INV-0042) by scanning existing invoices."""
        max_number = 0
        # Extract trailing digits from invoice numbers
        pattern = re.compile(r"(\d+)$")

        for value in Invoice.objects.values_list("invoice_number", flat=True):
            if not value:
                continue
            match = pattern.search(value)
            if match:
                max_number = max(max_number, int(match.group(1)))

        return f"INV-{max_number + 1:04d}"

    def _apply_widget_classes(self):
        """Applies consistent Tailwind CSS classes to all form field widgets."""
        base_class = "w-full px-4 py-3 border-2 border-gray-200 rounded-lg text-gray-800 bg-white focus:outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
        text_area_class = f"{base_class} min-h-[120px]"

        for name, field in self.fields.items():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("class", text_area_class)
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.setdefault(
                    "class", f"{base_class} appearance-none pr-10")
            else:
                field.widget.attrs.setdefault("class", base_class)

            if name == "invoice_number":
                field.widget.attrs.setdefault("class", base_class)
                field.widget.attrs.setdefault("readonly", "readonly")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_widget_classes()

        # Auto-fill the next invoice number for new invoices
        if self.instance and self.instance._state.adding:
            self.fields["invoice_number"].initial = self._next_invoice_number()

        # Pre-fill client fields when editing an existing invoice
        if self.instance and not self.instance._state.adding and self.instance.client_id:
            client = self.instance.client
            self.fields["business"].initial = client.business
            self.fields["client_name"].initial = client.name
            self.fields["client_email"].initial = client.email
            self.fields["address_line_1"].initial = client.address_line_1
            self.fields["address_line_2"].initial = client.address_line_2
            self.fields["city"].initial = client.city
            self.fields["state"].initial = client.state
            self.fields["pincode"].initial = client.pincode
            self.fields["country"].initial = client.country

    def save(self, commit=True):
        """Custom save: creates/updates both the Invoice and its linked Client in one step."""
        invoice = super().save(commit=False)
        business = self.cleaned_data["business"]

        # Auto-assign invoice number if blank
        if not invoice.invoice_number:
            invoice.invoice_number = self._next_invoice_number()

        # Reuse existing client on update, create new client on create
        if invoice.pk:
            client = invoice.client
        else:
            client = Client()

        # Populate client fields from form data
        client.business = business
        client.name = self.cleaned_data["client_name"]
        client.email = self.cleaned_data["client_email"]
        client.address_line_1 = self.cleaned_data["address_line_1"]
        client.address_line_2 = self.cleaned_data.get("address_line_2")
        client.city = self.cleaned_data["city"]
        client.state = self.cleaned_data["state"]
        client.pincode = self.cleaned_data["pincode"]
        client.country = self.cleaned_data["country"]
        client.save()

        invoice.client = client
        if commit:
            invoice.save()
        return invoice
