from decimal import Decimal

from django.db import models
from core.models import BaseModel, ContactInfoModel
from businesses.models import Business


# A client belongs to a business — the person/company being invoiced
class Client(BaseModel, ContactInfoModel):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='clients')  # Which business owns this client
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} (Client of {self.business.name})"


# An invoice sent to a client — status is computed from its milestones
class Invoice(BaseModel):
    # PROTECT prevents deleting client with existing invoices
    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name='invoices')
    invoice_number = models.CharField(
        max_length=50, unique=True)  # e.g., INV-0001
    notes = models.TextField(blank=True)  # Optional notes shown on the invoice

    @property
    def total_amount(self) -> Decimal:
        """Sum of all line items (quantity * unit_price)"""
        return sum((item.line_total for item in self.items.all()), Decimal('0'))

    @property
    def status(self) -> str:
        """
        Derives invoice status from milestone payment states:
        DRAFT → no milestones yet
        PAID → all milestones paid
        OVERDUE → any milestone overdue
        PARTIALLY_PAID → some paid, some not
        PENDING → milestones exist but none paid/overdue
        """
        milestones = self.milestones.all()
        if not milestones:
            return "DRAFT"

        if all(m.status == 'PAID' for m in milestones):
            return "PAID"

        if any(m.status == 'OVERDUE' for m in milestones):
            return "OVERDUE"

        if any(m.status == 'PAID' for m in milestones):
            return "PARTIALLY_PAID"

        return "PENDING"


# A line item on an invoice (e.g., "Website Design x1 @ ₹5000")
class InvoiceItem(BaseModel):
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def line_total(self) -> Decimal:
        """Calculated total for this line item"""
        return self.quantity * self.unit_price


# A payment milestone tied to an invoice (tracks partial payments and due
# dates)
class Milestone(BaseModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name='milestones')
    # e.g., "50% Deposit", "Final Payment"
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()                     # When this payment is due
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING')


# Pre-saved line items a business can quickly add to invoices
class DraftItem(BaseModel):
    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        related_name='draft_items')
    description = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
