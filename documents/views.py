import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from documents.models import Asset
from documents.serializers import AssetUploadSerializer, AssetListSerializer
from nlp_engine.hybrid import final_classification
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_asset(request):
    """
    Upload a new digital asset.

    POST /api/documents/upload/

    Form data:
        title            : string (required)
        description      : string (optional)
        asset_type       : document | image | video | note |
                           financial | social | other
        file             : the actual file (optional)
        content          : text content (optional, for notes)
        privacy_level    : LOW | MEDIUM | HIGH
        posthumous_action: delete | transfer

    Returns the created asset with its S3 URL and NLP results.
    """

    serializer = AssetUploadSerializer(
        data=request.data,
        context={'request': request}
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    # Save the asset — assign to logged-in user
    asset = serializer.save(user=request.user)

    # ── Run NLP Analysis ──────────────────────────────────────────
    # Analyze the title + content for sensitivity
    text_to_analyze = asset.title
    if asset.content:
        text_to_analyze += " " + asset.content

    try:
        nlp_result = final_classification(text_to_analyze)

        # Update asset with NLP results
        asset.sensitivity_level = nlp_result['level']
        asset.nlp_score         = nlp_result['final_score']
        asset.nlp_analyzed      = True
        asset.save()

        logger.info(
            f"[upload] NLP analysis complete for asset "
            f"{asset.asset_id} | "
            f"level: {nlp_result['level']} | "
            f"score: {nlp_result['final_score']:.2f}"
        )

    except Exception as e:
        logger.error(
            f"[upload] NLP analysis failed for asset "
            f"{asset.asset_id}: {e}"
        )

    # ── Return Response ───────────────────────────────────────────
    return Response(
        AssetUploadSerializer(
            asset,
            context={'request': request}
        ).data,
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_assets(request):
    """
    List all assets belonging to the logged-in user.

    GET /api/documents/

    Optional query params:
        ?type=document    filter by asset_type
        ?privacy=HIGH     filter by privacy_level
        ?sensitivity=HIGH filter by sensitivity_level
    """

    assets = Asset.objects.filter(
        user=request.user,
        deleted_at__isnull=True
    )

    # Apply filters if provided
    asset_type  = request.query_params.get('type')
    privacy     = request.query_params.get('privacy')
    sensitivity = request.query_params.get('sensitivity')

    if asset_type:
        assets = assets.filter(asset_type=asset_type)
    if privacy:
        assets = assets.filter(privacy_level=privacy)
    if sensitivity:
        assets = assets.filter(sensitivity_level=sensitivity)

    serializer = AssetListSerializer(
        assets,
        many=True,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_asset(request, asset_id):
    """
    Get a single asset by ID.

    GET /api/documents/<asset_id>/
    """

    try:
        asset = Asset.objects.get(
            asset_id=asset_id,
            user=request.user,
            deleted_at__isnull=True
        )
    except Asset.DoesNotExist:
        return Response(
            {"error": "Asset not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = AssetUploadSerializer(
        asset,
        context={'request': request}
    )
    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_asset(request, asset_id):
    """
    Soft delete an asset (marks deleted_at, doesn't remove from S3).

    DELETE /api/documents/<asset_id>/delete/
    """

    try:
        asset = Asset.objects.get(
            asset_id=asset_id,
            user=request.user,
            deleted_at__isnull=True
        )
    except Asset.DoesNotExist:
        return Response(
            {"error": "Asset not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    from django.utils import timezone
    asset.deleted_at = timezone.now()
    asset.save()

    logger.info(
        f"[delete] Asset {asset_id} soft deleted "
        f"by user {request.user.username}"
    )

    return Response(
        {"message": "Asset deleted successfully."},
        status=status.HTTP_200_OK
    )

# ================================================================
# DEATH CERTIFICATE UPLOAD
# ⚠️ ABSHER INTEGRATION — BUILT BUT NOT ACTIVATED
# ================================================================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_death_certificate(request):
    """
    ⚠️ ABSHER INTEGRATION — NOT ACTIVATED
    Built and ready but disabled until Absher API access
    is granted.

    Allows a beneficiary or admin to upload a death
    certificate for a specific user.

    POST /api/documents/death-certificate/

    Form data:
        user_id           : ID of the deceased user
        certificate       : the certificate file
        absher_reference  : Absher reference number (optional)
    """

    # ── ABSHER GATE — remove this block to activate ───────────────
    return Response(
        {
            "status":  "not_activated",
            "message": (
                "Death certificate upload via Absher is not "
                "yet activated. Awaiting Absher API access. "
                "This feature is built and ready to enable."
            ),
            "code": "ABSHER_NOT_ACTIVATED"
        },
        status=status.HTTP_503_SERVICE_UNAVAILABLE
    )
    # ── END ABSHER GATE ───────────────────────────────────────────

    # Everything below is ready but won't run until gate is removed

    user_id          = request.data.get('user_id')
    certificate_file = request.FILES.get('certificate')
    absher_reference = request.data.get('absher_reference')

    # Validate inputs
    if not user_id:
        return Response(
            {"error": "user_id is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not certificate_file:
        return Response(
            {"error": "Certificate file is required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Find the user
    try:
        deceased_user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response(
            {"error": "User not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Process the certificate
    from documents.death_verification import process_death_certificate
    try:
        process_death_certificate(
            user=deceased_user,
            certificate_file=certificate_file,
            absher_reference=absher_reference
        )
        return Response(
            {
                "status":  "success",
                "message": "Death certificate received. "
                           "Verification process started."
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(
            f"[death_certificate] Error processing "
            f"certificate: {e}"
        )
        return Response(
            {"error": "Failed to process certificate."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_beneficiary(request):
    """
    Add a beneficiary for the logged-in user.

    POST /api/documents/beneficiary/add/

    Body:
        name         : string
        email        : string
        phone        : string (optional)
        relationship : spouse | child | parent |
                       sibling | friend | other
    """
    from documents.models import Beneficiary

    name         = request.data.get('name')
    email        = request.data.get('email')
    phone        = request.data.get('phone')
    relationship = request.data.get('relationship', 'other')

    if not name or not email:
        return Response(
            {"error": "name and email are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    beneficiary = Beneficiary.objects.create(
        user=request.user,
        name=name,
        email=email,
        phone=phone,
        relationship=relationship
    )

    return Response(
        {
            "status": "success",
            "message": f"Beneficiary {name} added successfully.",
            "beneficiary_id": beneficiary.id,
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_asset_to_beneficiary(request):
    """
    Assign an asset to a beneficiary.

    POST /api/documents/beneficiary/assign/

    Body:
        asset_id       : UUID of the asset
        beneficiary_id : ID of the beneficiary
    """
    from documents.models import Beneficiary, AssetBeneficiary

    asset_id       = request.data.get('asset_id')
    beneficiary_id = request.data.get('beneficiary_id')

    if not asset_id or not beneficiary_id:
        return Response(
            {"error": "asset_id and beneficiary_id are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Verify asset belongs to user
    try:
        asset = Asset.objects.get(
            asset_id=asset_id,
            user=request.user
        )
    except Asset.DoesNotExist:
        return Response(
            {"error": "Asset not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Verify beneficiary belongs to user
    try:
        beneficiary = Beneficiary.objects.get(
            id=beneficiary_id,
            user=request.user
        )
    except Beneficiary.DoesNotExist:
        return Response(
            {"error": "Beneficiary not found."},
            status=status.HTTP_404_NOT_FOUND
        )

    # Create assignment
    assignment, created = AssetBeneficiary.objects.get_or_create(
        asset=asset,
        beneficiary=beneficiary
    )

    if not created:
        return Response(
            {"message": "Asset already assigned to this beneficiary."},
            status=status.HTTP_200_OK
        )

    # Update asset posthumous action to transfer
    asset.posthumous_action = 'transfer'
    asset.save()

    return Response(
        {
            "status":  "success",
            "message": f"Asset '{asset.title}' assigned to "
                       f"{beneficiary.name}.",
        },
        status=status.HTTP_201_CREATED
    )