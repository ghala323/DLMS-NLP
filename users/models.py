from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """
    Extends Django's built-in User model with DLMS-specific fields.
    Automatically created when a new User is created.

    Why we use a separate profile instead of changing User:
    - Django's User model is used by many packages
    - Safer to extend it than modify it
    - One-to-one relationship means profile.user gives us the User
      and user.profile gives us the UserProfile
    """

    # Link to Django's built-in User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    # Phone number for SMS notifications
    # Format: +966XXXXXXXXX (Saudi format)
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # National ID (for Nafath integration)
    national_id = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        unique=True
    )

    # Account status
    STATUS_CHOICES = [
        ('active',            'Active'),
        ('inactive',          'Inactive'),
        ('presumed_deceased', 'Presumed Deceased'),
        ('confirmed_deceased','Confirmed Deceased'),
    ]
    account_status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='active'
    )

    # Inactivity threshold in days (default 180 = 6 months)
    inactivity_threshold_days = models.IntegerField(default=180)

    # When the death verification process was triggered
    death_verification_triggered_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # When death was officially confirmed
    death_confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username} | {self.account_status}"

    def is_deceased(self):
        """Returns True if user is presumed or confirmed deceased."""
        return self.account_status in [
            'presumed_deceased',
            'confirmed_deceased'
        ]


# ── Auto-create profile when User is created ─────────────────────
# This signal fires every time a new User object is saved
# So every user automatically gets a profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Creates a UserProfile automatically when a User is created."""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Saves the UserProfile when the User is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()