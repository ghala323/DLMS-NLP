from rest_framework import serializers
from .models import DigitalAsset


class DigitalAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = DigitalAsset
        fields = [
            'id',
            'asset_type',
            'posthumous_action',
            'privacy_level',
            'is_transfer_ready',
            'is_locked',
            'uploaded_date',
            'updated_date',
        ]
        read_only_fields = [
            'is_transfer_ready',
            'is_locked',
            'uploaded_date',
            'updated_date',
        ]