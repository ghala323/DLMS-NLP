from django.contrib.auth.models import AbstractUser
from django.db import models


class Member(AbstractUser):
    national_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=20, blank=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='member_set',
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='member_set',
        blank=True
    )

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['national_id', 'email']

    def __str__(self):
        return f"{self.username} ({self.national_id})"


class DigitalAsset(models.Model):

    ASSET_TYPES = [
        ('DOCUMENT', 'Document'),
        ('PHOTO', 'Photo'),
        ('VIDEO', 'Video'),
    ]

    POSTHUMOUS_ACTIONS = [
        ('DELETE', 'Delete'),
        ('TRANSFER', 'Transfer'),
        ('PRIVATE', 'Private'),
    ]

    PRIVACY_LEVELS = [
        ('HIGH', 'High'),
        ('MODERATE', 'Moderate'),
        ('LOW', 'Low'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='assets'
    )
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    posthumous_action = models.CharField(max_length=20, choices=POSTHUMOUS_ACTIONS)
    privacy_level = models.CharField(max_length=20, choices=PRIVACY_LEVELS)
    is_transfer_ready = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    uploaded_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.asset_type} - {self.member.username}"


class Beneficiary(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='beneficiaries'
    )
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    national_id = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50)
    assets = models.ManyToManyField(
        DigitalAsset,
        blank=True,
        related_name='beneficiaries'
    )

    def __str__(self):
        return f"{self.name} - beneficiary of {self.member.username}"


class DeathConfirmation(models.Model):
    member = models.OneToOneField(
        Member,
        on_delete=models.CASCADE,
        related_name='death_confirmation'
    )
    absher_reference_number = models.CharField(max_length=100, blank=True)
    issue_status = models.CharField(max_length=20, default='PENDING')
    issue_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Death confirmation for {self.member.username}"


class Verification(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    verification_code = models.CharField(max_length=10)
    verification_status = models.CharField(max_length=20, default='PENDING')
    sent_via = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Verification for {self.member.username}"


class UserActivity(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='activities'
    )
    asset = models.ForeignKey(
        DigitalAsset,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    activity_type = models.CharField(max_length=50)
    activity_status = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.activity_type} - {self.member.username}"