import re

from rest_framework import serializers

from billings.models import Client, Invoice, InvoiceItem, Milestone, DraftItem
from businesses.models import Business


# ── Client Serializer ───────────────────────────────────────────────────


class ClientSerializer(serializers.ModelSerializer):
    """Serializer for client data (the person/company being invoiced)."""

    class Meta:
        model = Client
        fields = [
            'id', 'business', 'name', 'email',
            'address_line_1', 'address_line_2', 'city', 'state',
            'pincode', 'country', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


# ── Invoice Line Item Serializer ────────────────────────────────────────


class InvoiceItemSerializer(serializers.ModelSerializer):
    """Serializer for individual line items on an invoice."""

    # Expose the computed @property (quantity * unit_price)
    line_total = serializers.ReadOnlyField()

    class Meta:
        model = InvoiceItem
        fields = ['id', 'description', 'quantity', 'unit_price', 'line_total']
        read_only_fields = ['id']


# ── Milestone Serializer ────────────────────────────────────────────────


class MilestoneSerializer(serializers.ModelSerializer):
    """Serializer for payment milestones (partial payments with due dates)."""

    class Meta:
        model = Milestone
        fields = ['id', 'description', 'amount', 'due_date', 'status']
        read_only_fields = ['id']


# ── Invoice Serializers ─────────────────────────────────────────────────


class InvoiceSerializer(serializers.ModelSerializer):
    """
    Full invoice detail serializer with nested items, milestones, and client.
    Used for the retrieve (GET detail) view.
    """

    # Nested read-only representations
    items = InvoiceItemSerializer(many=True, read_only=True)
    milestones = MilestoneSerializer(many=True, read_only=True)
    client = ClientSerializer(read_only=True)
    # Computed @property fields from the Invoice model
    status = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()

    class Meta:
        model = Invoice
        fields = [
            'id', 'client', 'invoice_number', 'notes', 'status',
            'total_amount', 'items', 'milestones', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class InvoiceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for paginated invoice listings."""

    # Computed @property fields
    status = serializers.ReadOnlyField()
    total_amount = serializers.ReadOnlyField()
    # Flatten nested relations for a compact list representation
    client_name = serializers.ReadOnlyField(source='client.name')
    business_name = serializers.ReadOnlyField(source='client.business.name')

    class Meta:
        model = Invoice
        fields = [
            'id', 'invoice_number', 'client_name', 'business_name',
            'status', 'total_amount', 'created_at',
        ]


class InvoiceCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Creates/updates an invoice together with its linked client, line items,
    and milestones — mirrors the original InvoiceForm logic.
    """

    # Inline client fields (stored on the Client model, not Invoice)
    business = serializers.PrimaryKeyRelatedField(
        queryset=Business.objects.all(),
        help_text='UUID of the business this invoice belongs to.',
    )
    client_name = serializers.CharField(max_length=255)
    client_email = serializers.EmailField()
    address_line_1 = serializers.CharField(max_length=255)
    address_line_2 = serializers.CharField(
        max_length=255, required=False, allow_blank=True, default='')
    city = serializers.CharField(max_length=100)
    state = serializers.CharField(max_length=100)
    pincode = serializers.CharField(max_length=10)
    country = serializers.CharField(max_length=100, default='India')

    # Nested writable items and milestones
    items = InvoiceItemSerializer(many=True, required=False)
    milestones = MilestoneSerializer(many=True, required=False)

    class Meta:
        model = Invoice
        fields = [
            'invoice_number', 'notes', 'business',
            'client_name', 'client_email',
            'address_line_1', 'address_line_2', 'city', 'state',
            'pincode', 'country', 'items', 'milestones',
        ]

    # ── Auto-increment invoice number ───────────────────────────────────

    @staticmethod
    def _next_invoice_number():
        """Auto-generates the next sequential invoice number (e.g., INV-0042)."""
        max_number = 0
        pattern = re.compile(r'(\d+)$')
        for value in Invoice.objects.values_list('invoice_number', flat=True):
            if not value:
                continue
            match = pattern.search(value)
            if match:
                max_number = max(max_number, int(match.group(1)))
        return f'INV-{max_number + 1:04d}'

    # ── Create ──────────────────────────────────────────────────────────

    def create(self, validated_data):
        """Creates the Client, Invoice, InvoiceItems, and Milestones in one step."""
        items_data = validated_data.pop('items', [])
        milestones_data = validated_data.pop('milestones', [])
        business = validated_data.pop('business')

        # Build the client from inline fields
        client = Client.objects.create(
            business=business,
            name=validated_data.pop('client_name'),
            email=validated_data.pop('client_email'),
            address_line_1=validated_data.pop('address_line_1'),
            address_line_2=validated_data.pop('address_line_2', ''),
            city=validated_data.pop('city'),
            state=validated_data.pop('state'),
            pincode=validated_data.pop('pincode'),
            country=validated_data.pop('country', 'India'),
        )

        # Auto-assign invoice number if not provided
        if not validated_data.get('invoice_number'):
            validated_data['invoice_number'] = self._next_invoice_number()

        invoice = Invoice.objects.create(client=client, **validated_data)

        # Create nested line items
        for item_data in items_data:
            InvoiceItem.objects.create(invoice=invoice, **item_data)

        # Create nested milestones
        for milestone_data in milestones_data:
            Milestone.objects.create(invoice=invoice, **milestone_data)

        return invoice

    # ── Update ──────────────────────────────────────────────────────────

    def update(self, instance, validated_data):
        """Updates the Invoice and its linked Client; replaces items/milestones if provided."""
        items_data = validated_data.pop('items', None)
        milestones_data = validated_data.pop('milestones', None)
        business = validated_data.pop('business', None)

        # ── Update client fields ────────────────────────────────────────
        client = instance.client
        if business:
            client.business = business
        # Map serializer field names to Client model field names
        client_field_map = {
            'client_name': 'name',
            'client_email': 'email',
            'address_line_1': 'address_line_1',
            'address_line_2': 'address_line_2',
            'city': 'city',
            'state': 'state',
            'pincode': 'pincode',
            'country': 'country',
        }
        for serializer_field, model_field in client_field_map.items():
            if serializer_field in validated_data:
                setattr(client, model_field, validated_data.pop(serializer_field))
        client.save()

        # ── Update invoice fields ───────────────────────────────────────
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # ── Replace line items (full replacement if provided) ───────────
        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                InvoiceItem.objects.create(invoice=instance, **item_data)

        # ── Replace milestones (full replacement if provided) ───────────
        if milestones_data is not None:
            instance.milestones.all().delete()
            for milestone_data in milestones_data:
                Milestone.objects.create(invoice=instance, **milestone_data)

        return instance


# ── Draft Item Serializer ───────────────────────────────────────────────


class DraftItemSerializer(serializers.ModelSerializer):
    """Pre-saved line items that businesses can quickly add to invoices."""

    class Meta:
        model = DraftItem
        fields = [
            'id', 'business', 'description', 'unit_price',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
