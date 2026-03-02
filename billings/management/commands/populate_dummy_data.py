import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import CustomUser
from businesses.models import Business
from billings.models import Client, Invoice, InvoiceItem, Milestone


class Command(BaseCommand):
    """
    Management command to seed the database with realistic test data.
    Run with: python manage.py populate_dummy_data
    Creates: 1 test user, 3 businesses, 5 clients per business, 2 invoices per client (30 total).
    """
    help = 'Populates the database with dummy data (Businesses, Clients, Invoices)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')

        # 1. Create test user (or reuse if already exists)
        user, created = CustomUser.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'is_staff': True,  # Allows admin panel access
                'first_name': 'Test',
                'last_name': 'User',
                'phone_number': '1234567890'
            }
        )
        if created:
            user.set_password('password123')  # Default test password
            user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Created user: {
                        user.username} (password: password123)'))

        # 2. Create 3 sample businesses owned by the test user
        business_names = [
            'TechNova Solutions',
            'GreenLeaf Designs',
            'Quantum Logistics']
        businesses = []
        for name in business_names:
            biz, created = Business.objects.get_or_create(
                owner=user,
                name=name,
                defaults={
                    'email': f'contact@{name.lower().replace(" ", "")}.com',
                    'gstin': f'22AAAAA{random.randint(1000, 9999)}A1Z5',
                    'address_line_1': '123 Business Park',
                    'city': 'Mumbai',
                    'state': 'Maharashtra',
                    'country': 'India',
                    'brand_color': '#4f46e5'
                }
            )
            businesses.append(biz)

        self.stdout.write(f'Ensured {len(businesses)} businesses exist.')

        # 3. Create clients and invoices for each business
        client_names = [
            'Alpha Corp',
            'Beta Ltd',
            'Gamma Inc',
            'Delta LLC',
            'Epsilon Group']

        total_invoices = 0

        for biz in businesses:
            for i, c_name in enumerate(client_names):
                # Create a client scoped to each business (e.g., "Alpha Corp
                # (TechNova)")
                client, _ = Client.objects.get_or_create(
                    business=biz,
                    name=f"{c_name} ({biz.name.split()[0]})",
                    defaults={
                        'email': f'accounts@{c_name.lower().replace(" ", "")}.com',
                        'address_line_1': f'{random.randint(1, 999)} Market St',
                        'city': 'Bangalore',
                        'state': 'Karnataka',
                        'country': 'India'
                    }
                )

                # Create 2 invoices per client with sequential invoice numbers
                for j in range(1, 3):
                    # Generate sequential invoice number (INV-0001, INV-0002,
                    # ...)
                    last_invoice = Invoice.objects.all().order_by('-invoice_number').first()
                    if last_invoice and last_invoice.invoice_number.startswith(
                            'INV-'):
                        try:
                            last_num = int(
                                last_invoice.invoice_number.split('-')[1])
                            inv_number = f"INV-{last_num + 1:04d}"
                        except (ValueError, IndexError):
                            inv_number = f"INV-{Invoice.objects.count() + 1:04d}"
                    else:
                        inv_number = f"INV-{Invoice.objects.count() + 1:04d}"

                    if Invoice.objects.filter(
                            invoice_number=inv_number).exists():
                        continue

                    invoice = Invoice.objects.create(
                        client=client,
                        invoice_number=inv_number,
                        notes="Thank you for your business!",
                    )
                    # Backdate created_at for realistic timeline data on the
                    # dashboard
                    invoice.created_at = timezone.now() - timedelta(days=random.randint(0, 60))
                    invoice.save(update_fields=['created_at'])

                    # Create a single line item per invoice
                    item_amount = Decimal(random.randint(5000, 50000))
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description="Professional Services",
                        quantity=1,
                        unit_price=item_amount
                    )

                    # Create a milestone with random status (this drives
                    # invoice status)
                    status = random.choice(['PAID', 'PENDING', 'OVERDUE'])
                    Milestone.objects.create(
                        invoice=invoice,
                        description="Full Payment",
                        amount=item_amount,
                        due_date=timezone.now() + timedelta(days=random.randint(-10, 20)),
                        status=status
                    )
                    total_invoices += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated database with {total_invoices} new invoices.'))
