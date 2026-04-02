from rest_framework.permissions import BasePermission
from .services import AccessControlService
 
 
class AssetAccessPermission(BasePermission):
    """
    Used on: AssetDetailView (GET /assets/<id>/)
 
    Allows:
    - The asset's owner (if alive)
    - A verified beneficiary of that specific asset (if owner is confirmed dead
      and asset policy is TRANSFER)
 
    Logs every attempt (granted or denied) to UserActivity.
    """
 
    message = "You do not have permission to access this asset."
 
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
 
    def has_object_permission(self, request, view, obj):
        member = request.user
        granted = AccessControlService.can_access_asset(member, obj)
        AccessControlService.log_access_attempt(member, obj, granted)
        return granted
 
 
class IsOwnerPermission(BasePermission):
    """
    Used on: AssetEditView, AssetDeleteView
 
    Only the asset's owner may edit or delete.
    Dead owners are blocked — AccessControlService.can_access_asset handles
    that case, but we also guard it explicitly here for the write paths.
    """
 
    message = "Only the asset owner can perform this action."
 
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
 
    def has_object_permission(self, request, view, obj):
        member = request.user
 
        if obj.member_id != member.member_id:
            return False
 
        # Deceased owners cannot modify assets
        if AccessControlService.death_verified(member):
            return False
 
        return True
 
 
class BeneficiaryAccessPermission(BasePermission):
    """
    Used on: BeneficiaryAssetAccessView (GET /assets/<id>/beneficiary-access/)
 
    Stricter than AssetAccessPermission — only beneficiaries, never owners.
    Requires:
    1. Owner's death is confirmed.
    2. Requester is listed as a beneficiary of this specific asset.
    3. Requester has passed recent identity verification.
    """
 
    message = "Beneficiary access denied."
 
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
 
    def has_object_permission(self, request, view, obj):
        member = request.user
 
        # Step 1: Owner must be confirmed dead
        if not AccessControlService.death_verified(obj.member):
            return False
 
        # Step 2: Must be a beneficiary assigned to this specific asset
        if not AccessControlService.is_beneficiary_of(member.national_id, obj):
            return False
 
        # Step 3: Must have passed recent identity verification
        if not AccessControlService.verification_passed(member):
            return False
 
        return True