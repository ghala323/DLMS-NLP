import logging
from datetime import timedelta

from django.utils import timezone

from ACL.models import DigitalAsset, Beneficiary, DeathConfirmation, Verification, UserActivity
from .policies import AssetPolicy

logger = logging.getLogger(__name__)


class AccessControlService:

    # How long a verification token stays valid
    VERIFICATION_WINDOW_HOURS = 24

    @staticmethod
    def is_owner(member, asset):
        return asset.member_id == member.id

    @staticmethod
    def death_verified(member):
        return DeathConfirmation.objects.filter(
            member=member,
            issue_status="VERIFIED"
        ).exists()

    @staticmethod
    def is_beneficiary_of(requester_national_id, asset):
        """
        Check if the requester is a beneficiary assigned specifically to THIS asset.
        Identity is matched by national_id — not email — as national_id is the
        authoritative identifier used by Absher/Nafath for Saudi nationals.
        Matches the ERD's Sent_to relationship between Digital_Asset and Beneficiary.
        """
        return Beneficiary.objects.filter(
            member=asset.member,
            national_id=requester_national_id,
            assets=asset
        ).exists()

    @staticmethod
    def verification_passed(member):
        """
        Verification must be recent (within VERIFICATION_WINDOW_HOURS).
        This prevents old verification tokens granting permanent access.
        """
        cutoff = timezone.now() - timedelta(
            hours=AccessControlService.VERIFICATION_WINDOW_HOURS
        )
        return Verification.objects.filter(
            member=member,
            verification_status="VERIFIED",
            timestamp__gte=cutoff
        ).exists()

    @staticmethod
    def can_access_asset(member, asset):
        """
        Central access decision method.

        Rules (evaluated in order):
        1. Owner can access only if alive.
        2. Non-owners cannot access if owner is alive.
        3. Requester must be a designated beneficiary of this specific asset.
        4. Requester must have passed identity verification recently.
        5. Asset's posthumous policy must allow access (TRANSFER only).
        """

        # RULE 1: Owner access — only if alive
        if AccessControlService.is_owner(member, asset):
            if AccessControlService.death_verified(member):
                return False
            return True

        # RULE 2: Owner must be confirmed dead before anyone else can access
        if not AccessControlService.death_verified(asset.member):
            return False

        # RULE 3: Requester must be a beneficiary assigned to this asset
        if not AccessControlService.is_beneficiary_of(member.national_id, asset):
            return False

        # RULE 4: Requester must have passed recent identity verification
        if not AccessControlService.verification_passed(member):
            return False

        # RULE 5: Apply posthumous policy
        if AssetPolicy.should_delete(asset):
            return False

        if AssetPolicy.can_transfer(asset):
            return True

        if AssetPolicy.is_private(asset):
            return True

        # Unknown / unhandled policy — deny by default
        return False

    @staticmethod
    def log_access_attempt(member, asset, granted):
        """
        Records every access attempt (granted or denied) for audit purposes.
        Failures are logged to the error log but never raise — access decision
        already happened and must not be affected by a logging failure.
        """
        try:
            UserActivity.objects.create(
                member=member,
                asset=asset,
                activity_type="ASSET_ACCESS",
                activity_status="GRANTED" if granted else "DENIED"
            )
        except Exception as e:
            logger.error(
                "Failed to log access attempt for member=%s asset=%s granted=%s: %s",
                getattr(member, "member_id", "?"),
                getattr(asset, "asset_id", "?"),
                granted,
                e,
            )