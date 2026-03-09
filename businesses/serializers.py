from rest_framework import serializers

from businesses.models import Business


# ── Business Serializers ────────────────────────────────────────────────


class BusinessSerializer(serializers.ModelSerializer):
    """
    Full serializer for business CRUD operations.
    Used for detail, create, and update views.
    """

    # Display the owner's username instead of the UUID
    owner = serializers.ReadOnlyField(source='owner.username')
    # Expose the @property that safely returns the logo URL
    logo_url_safe = serializers.ReadOnlyField()

    class Meta:
        model = Business
        fields = [
            'id', 'owner', 'name', 'email', 'gstin', 'logo', 'brand_color',
            'address_line_1', 'address_line_2', 'city', 'state', 'pincode',
            'country', 'logo_url_safe', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class BusinessListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for paginated business listings."""

    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Business
        fields = ['id', 'name', 'email', 'owner', 'brand_color', 'created_at']
