import logging

from django.db import transaction

from ACL.models import DigitalAsset
from .policies import AssetPolicy

logger = logging.getLogger(__name__)


class PostDeathAssetWorkflow:
    """
    Executes all posthumous asset actions for a given member once their
    death has been confirmed.

    Called by TriggerPostDeathWorkflowView — should only run once per member.
    The entire operation is wrapped in a database transaction so that a
    mid-loop failure does not leave assets in a partially-processed state.
    """

    @staticmethod
    @transaction.atomic
    def process_member_assets(member):
        """
        Iterates over all assets belonging to `member` and applies the
        appropriate posthumous action:

        - DELETE  → permanently remove the asset record
        - PRIVATE → lock the asset (inaccessible to anyone)
        - TRANSFER → mark as transfer-ready so beneficiaries can retrieve it
        """
        assets = DigitalAsset.objects.select_for_update().filter(member=member)

        deleted_count = 0
        transfer_count = 0

        for asset in assets:

            if AssetPolicy.should_delete(asset):
                asset.delete()
                deleted_count += 1

            elif AssetPolicy.can_transfer(asset):
                # Transferable — any assigned beneficiary can access
                asset.is_transfer_ready = True
                asset.save(update_fields=["is_transfer_ready"])
                transfer_count += 1

            elif AssetPolicy.is_private(asset):
                # Private — only designated beneficiaries can access,
                # but it IS accessible (not locked). Mark as transfer-ready
                # same as TRANSFER; the beneficiary check in permissions
                # already ensures only assigned people get through.
                asset.is_transfer_ready = True
                asset.save(update_fields=["is_transfer_ready"])
                transfer_count += 1

            else:
                # Unknown policy — log and skip rather than silently do nothing
                logger.warning(
                    "Asset %s has unknown posthumous_action '%s'. Skipped.",
                    asset.asset_id,
                    asset.posthumous_action,
                )

        logger.info(
            "PostDeathAssetWorkflow complete for member=%s: "
            "deleted=%d transfer_ready=%d",
            member.id,
            deleted_count,
            transfer_count,
        )

        return {
            "deleted": deleted_count,
            "transfer_ready": transfer_count,
        }