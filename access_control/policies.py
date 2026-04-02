class AssetPolicy:

    # Posthumous actions
    DELETE = "DELETE"
    TRANSFER = "TRANSFER"
    PRIVATE = "PRIVATE"

    # Privacy levels (from system design)
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LOW = "LOW"

    @staticmethod
    def can_transfer(asset):
        return asset.posthumous_action == AssetPolicy.TRANSFER

    @staticmethod
    def should_delete(asset):
        return asset.posthumous_action == AssetPolicy.DELETE

    @staticmethod
    def is_private(asset):
        """
        PRIVATE means restricted to designated beneficiaries only.
        NOT inaccessible — specifically assigned beneficiaries can still
        access it after death confirmation.
        """
        return asset.posthumous_action == AssetPolicy.PRIVATE

    @staticmethod
    def get_privacy_label(asset):
        """
        Returns a human-readable privacy label based on the asset's privacy level.
        Useful for serializers and audit logs.
        """
        return {
            AssetPolicy.HIGH: "High Privacy",
            AssetPolicy.MODERATE: "Moderate Privacy",
            AssetPolicy.LOW: "Low Privacy",
        }.get(asset.privacy_level, "Unknown")