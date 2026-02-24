import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone

from businesses.models import Business
from billings.models import Client, Invoice, InvoiceItem, Milestone
from accounts.models import Profile

class Command(BaseCommand):
    help = 'Populates the database with dummy data (Businesses, Clients, Invoices)'

    def handle(self, *args, **kwargs):
        self.stdout.write('Starting data population...')

        # 1. Create User
        user, created = User.objects.get_or_create(
            username='testuser',
            defaults={'email': 'test@example.com', 'is_staff': True}
        )
        if created:
            user.set_password('password123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username} (password: password123)'))
        
        # Ensure profile exists
        Profile.objects.get_or_create(user=user, defaults={'phone_number': '1234567890'})

        # 2. Create Businesses
        business_names = ['TechNova Solutions', 'GreenLeaf Designs', 'Quantum Logistics']
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

        # 3. Create Clients and Invoices
        client_names = ['Alpha Corp', 'Beta Ltd', 'Gamma Inc', 'Delta LLC', 'Epsilon Group']
        
        total_invoices = 0

        for biz in businesses:
            for i, c_name in enumerate(client_names):
                # Create Client
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

                # Create 2 Invoices per client
                for j in range(1, 3):
                    inv_number = f"INV-{biz.id}-{client.id}-{j:03d}"
                    
                    if Invoice.objects.filter(invoice_number=inv_number).exists():
                        continue

                    invoice = Invoice.objects.create(
                        client=client,
                        invoice_number=inv_number,
                        notes="Thank you for your business!",
                    )
                    # Update created_at to be in the past for better graph data
                    invoice.created_at = timezone.now() - timedelta(days=random.randint(0, 60))
                    invoice.save(update_fields=['created_at'])

                    # Create Invoice Item
                    item_amount = Decimal(random.randint(5000, 50000))
                    InvoiceItem.objects.create(
                        invoice=invoice,
                        description="Professional Services",
                        quantity=1,
                        unit_price=item_amount
                    )
                    
                    # Create Milestone (This determines the status: PAID, PENDING, OVERDUE)
                    status = random.choice(['PAID', 'PENDING', 'OVERDUE'])
                    Milestone.objects.create(
                        invoice=invoice,
                        description="Full Payment",
                        amount=item_amount,
                        due_date=timezone.now() + timedelta(days=random.randint(-10, 20)),
                        status=status
                    )
                    total_invoices += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully populated database with {total_invoices} new invoices.'))