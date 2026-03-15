from django.db import models
from django.contrib.auth.models import User
import uuid


class Asset(models.Model):
    """
    Represents a digital asset uploaded by a user.
    Matches the Digital_Asset table from the DLMS capstone report.
    """

    # ── Asset Types ───────────────────────────────────────────────
    ASSET_TYPE_CHOICES = [
        ('document',    'Document (PDF, Word)'),
        ('image',       'Image (JPG, PNG)'),
        ('video',       'Video'),
        ('note',        'Text Note'),
        ('financial',   'Financial Document'),
        ('social',      'Social Media Archive'),
        ('other',       'Other'),
    ]

    # ── Posthumous Actions ────────────────────────────────────────
    POSTHUMOUS_ACTION_CHOICES = [
        ('delete',    'Delete after death'),
        ('transfer',  'Transfer to beneficiary'),
    ]

    # ── Privacy Levels ────────────────────────────────────────────
    PRIVACY_CHOICES = [
        ('LOW',    'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH',   'High'),
    ]

    # ── Sensitivity (set by NLP) ──────────────────────────────────
    SENSITIVITY_CHOICES = [
        ('LOW',    'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH',   'High'),
    ]

    # Unique ID
    asset_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    # Owner
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assets'
    )

    # Basic info
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    asset_type = models.CharField(
        max_length=20,
        choices=ASSET_TYPE_CHOICES,
        default='document'
    )

    # The actual file — stored in AWS S3
    # Files go to: s3://erth-dlms-assets/assets/user_{id}/filename
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        null=True,
        blank=True
    )

    # Text content (for text notes or extracted text)
    content = models.TextField(blank=True, null=True)

    # Privacy & sensitivity
    privacy_level = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default='MEDIUM'
    )
    sensitivity_level = models.CharField(
        max_length=10,
        choices=SENSITIVITY_CHOICES,
        default='LOW'
    )

    # NLP analysis results
    nlp_score = models.FloatField(default=0.0)
    nlp_analyzed = models.BooleanField(default=False)

    # Posthumous action
    posthumous_action = models.CharField(
        max_length=20,
        choices=POSTHUMOUS_ACTION_CHOICES,
        default='transfer'
    )

    # Timestamps
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    deleted_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.asset_type}) — {self.user.username}"

    def get_file_url(self):
        """Returns the S3 URL of the uploaded file."""
        if self.file:
            return self.file.url
        return None

class Beneficiary(models.Model):

    RELATIONSHIP_CHOICES = [
        ('spouse',  'Spouse'),
        ('child',   'Child'),
        ('parent',  'Parent'),
        ('sibling', 'Sibling'),
        ('friend',  'Friend'),
        ('other',   'Other'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='beneficiaries'
    )
    name         = models.CharField(max_length=200)
    email        = models.EmailField()
    phone        = models.CharField(max_length=20, blank=True, null=True)
    relationship = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_CHOICES,
        default='other'
    )
    access_code  = models.CharField(max_length=20, blank=True, null=True)
    has_accessed = models.BooleanField(default=False)
    created_at   = models.DateTimeField(auto_now_add=True)

    def _str_(self):
        return f"{self.name} ({self.relationship}) — {self.user.username}"


class AssetBeneficiary(models.Model):

    asset = models.ForeignKey(
        Asset,
        on_delete=models.CASCADE,
        related_name='asset_beneficiaries'
    )
    beneficiary = models.ForeignKey(
        Beneficiary,
        on_delete=models.CASCADE,
        related_name='assigned_assets'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('asset', 'beneficiary')

    def _str_(self):
        return f"{self.asset.title} → {self.beneficiary.name}"


class DeathVerification(models.Model):

    METHOD_CHOICES = [
        ('inactivity',  'Inactivity Monitoring'),
        ('no_response', 'No Response to Verification Messages'),
        ('certificate', 'Death Certificate (Absher)'),
    ]

    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='death_verification'
    )
    trigger_method      = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        default='inactivity'
    )
    status              = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    messages_sent       = models.IntegerField(default=0)
    messages_unanswered = models.IntegerField(default=0)

    # ⚠️ ABSHER — BUILT BUT NOT ACTIVATED
    death_certificate   = models.FileField(
        upload_to='death_certificates/',
        null=True,
        blank=True
    )
    absher_reference    = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )
    triggered_at        = models.DateTimeField(auto_now_add=True)
    confirmed_at        = models.DateTimeField(null=True, blank=True)
    cancelled_at        = models.DateTimeField(null=True, blank=True)

    def _str_(self):
        return (
            f"DeathVerification: {self.user.username} | "
            f"{self.status} | {self.trigger_method}"
        )