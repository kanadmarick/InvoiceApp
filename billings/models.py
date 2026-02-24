from django.db import models
from core.models import BaseModel, ContactInfoModel
from businesses.models import Business


class Client(BaseModel, ContactInfoModel):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='clients')
    name = models.CharField(max_length=255)
    email = models.EmailField()

    def __str__(self):
        return f"{self.name} (Client of {self.business.name})"


class Invoice(BaseModel):
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='invoices')
    invoice_number = models.CharField(max_length=50, unique=True)
    notes = models.TextField(blank=True)

    @property
    def total_amount(self):
        return sum(item.line_total for item in self.items.all())

    @property
    def status(self):
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


class InvoiceItem(BaseModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)

    @property
    def line_total(self):
        return self.quantity * self.unit_price


class Milestone(BaseModel):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('OVERDUE', 'Overdue'),
    ]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='milestones')
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')


class DraftItem(BaseModel):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='draft_items')
    description = models.CharField(max_length=255)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
