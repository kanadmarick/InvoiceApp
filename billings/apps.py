from django.apps import AppConfig


# App config for the billings module — handles invoices, clients,
# milestones, and draft items
class BillingsConfig(AppConfig):
    name = 'billings'
