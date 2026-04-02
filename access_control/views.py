from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView

from ACL.models import DigitalAsset, Member
from ACL.serializers import DigitalAssetSerializer

from .permissions import AssetAccessPermission, IsOwnerPermission, BeneficiaryAccessPermission
from .services import AccessControlService
from .workflow import PostDeathAssetWorkflow


class MemberAssetListView(generics.ListAPIView):
    """
    GET /assets/

    Returns only the assets belonging to the requesting member.
    Database-level filter — a member can never see another member's assets.
    """
    serializer_class = DigitalAssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DigitalAsset.objects.filter(member=self.request.user)


class AssetDetailView(generics.RetrieveAPIView):
    """
    GET /assets/<id>/

    Owner access: allowed if alive.
    Beneficiary access: use /assets/<id>/beneficiary-access/ instead.

    Returns 404 (not 403) if the asset does not belong to the requester's
    visible queryset — this prevents ID enumeration.
    """
    serializer_class = DigitalAssetSerializer
    permission_classes = [IsAuthenticated, AssetAccessPermission]

    def get_queryset(self):
        """
        Scope to assets the requesting user could plausibly own.
        has_object_permission will enforce the finer access rules.
        """
        return DigitalAsset.objects.filter(member=self.request.user)


class AssetEditView(generics.UpdateAPIView):
    """
    PUT/PATCH /assets/<id>/edit/

    Only the living owner can edit an asset.
    Deceased owners are blocked by IsOwnerPermission.
    """
    serializer_class = DigitalAssetSerializer
    permission_classes = [IsAuthenticated, IsOwnerPermission]

    def get_queryset(self):
        return DigitalAsset.objects.filter(member=self.request.user)


class AssetDeleteView(generics.DestroyAPIView):
    """
    DELETE /assets/<id>/delete/

    Only the living owner can delete an asset manually.
    Posthumous deletion is handled by PostDeathAssetWorkflow, not this view.
    """
    serializer_class = DigitalAssetSerializer
    permission_classes = [IsAuthenticated, IsOwnerPermission]

    def get_queryset(self):
        return DigitalAsset.objects.filter(member=self.request.user)


class BeneficiaryAssetAccessView(generics.RetrieveAPIView):
    """
    GET /assets/<id>/beneficiary-access/

    Dedicated endpoint for beneficiaries to retrieve an asset after the
    owner's death has been confirmed.

    Requirements (enforced by BeneficiaryAccessPermission):
    - Owner's death is confirmed (DeathConfirmation.issue_status = VERIFIED)
    - Requester is assigned as a beneficiary of this specific asset
    - Requester has passed recent identity verification (within 24 hours)
    - Asset's posthumous_action must be TRANSFER
    """
    serializer_class = DigitalAssetSerializer
    permission_classes = [IsAuthenticated, BeneficiaryAccessPermission]

    def get_queryset(self):
        # All assets are reachable here — beneficiary may not own the asset.
        # BeneficiaryAccessPermission enforces all access rules at object level.
        return DigitalAsset.objects.all()


class TriggerPostDeathWorkflowView(APIView):
    """
    POST /members/<pk>/process-death/

    Triggers posthumous asset processing for a confirmed-dead member.
    Restricted to admin users only — in production this would be called
    by the Absher integration webhook, not directly by users.

    Returns a summary of actions taken:
    {
        "deleted": <int>,
        "locked": <int>,
        "transfer_ready": <int>
    }
    """
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, pk):
        try:
            member = Member.objects.get(pk=pk)
        except Member.DoesNotExist:
            return Response(
                {"detail": "Member not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if not AccessControlService.death_verified(member):
            return Response(
                {"detail": "Death has not been verified for this member."},
                status=status.HTTP_400_BAD_REQUEST
            )

        summary = PostDeathAssetWorkflow.process_member_assets(member)

        return Response(summary, status=status.HTTP_200_OK)