content = open('users/models.py', 'r', encoding='utf-8').read()

new_content = """from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from encrypted_model_fields.fields import EncryptedCharField


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = EncryptedCharField(max_length=255, blank=True, null=True)
    national_id = EncryptedCharField(max_length=255, blank=True, null=True)
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('presumed_deceased', 'Presumed Deceased'),
        ('confirmed_deceased', 'Confirmed Deceased'),
    ]
    account_status = models.CharField(
        max_length=25,
        choices=STATUS_CHOICES,
        default='active'
    )
    inactivity_threshold_days = models.IntegerField(default=180)
    death_verification_triggered_at = models.DateTimeField(
        null=True, blank=True
    )
    death_confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def _str_(self):
        return f"Profile: {self.user.username} | {self.account_status}"

    def is_deceased(self):
        return self.account_status in [
            'presumed_deceased',
            'confirmed_deceased'
        ]


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
"""

with open('users/models.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Done!')