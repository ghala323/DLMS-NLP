import logging
import secrets
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from documents.models import (
    Beneficiary,
    AssetBeneficiary,
    Asset,
    DeathVerification
)
from users.models import UserProfile
from notifications.dispatcher import dispatch
from notifications.scheduler import notify_beneficiary

logger = logging.getLogger(__name__)


def check_user_inactivity(user):
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=user)

    if profile.is_deceased():
        return 'already_deceased'

    if not user.last_login:
        return 'active'

    now = timezone.now()
    last_login = user.last_login
    days_inactive = (now - last_login).days
    threshold = profile.inactivity_threshold_days
    days_left = threshold - days_inactive

    if days_left in [90, 30, 7]:
        _send_verification_warning(user, days_inactive, days_left)
        return 'warning_sent'
    elif days_inactive >= threshold:
        _trigger_death_verification(user, days_inactive)
        return 'death_triggered'

    return 'active'


def _send_verification_warning(user, days_inactive, days_left):
    from notifications.models import VerificationAttempt
    from django.conf import settings

    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timezone.timedelta(hours=48)

    VerificationAttempt.objects.create(
        user=user,
        token=token,
        expires_at=expires_at
    )

    base_url = getattr(settings, 'APP_BASE_URL', 'http://localhost:8000')
    confirm_url = f"{base_url}/notifications/alive/{token}/"

    if days_left == 90:
        template = 'INACTIVITY_WARNING_90'
    elif days_left == 30:
        template = 'INACTIVITY_WARNING_30'
    else:
        template = 'INACTIVITY_WARNING_7'

    phone = getattr(user.profile, 'phone', None)

    dispatch(
        template_code=template,
        template_data={
            'name': user.get_full_name() or user.username,
            'days_inactive': days_inactive,
            'days_left': days_left,
            'confirm_url': confirm_url,
        },
        recipient={
            'email': user.email,
            'phone': phone,
            'user_id': user.id,
        },
        channels=['email', 'sms', 'in_app'],
        user=user,
        recipient_type='user'
    )


def _trigger_death_verification(user, days_inactive):
    existing = DeathVerification.objects.filter(
        user=user,
        status='pending'
    ).first()

    if existing:
        return

    DeathVerification.objects.create(
        user=user,
        trigger_method='inactivity',
        status='pending',
        messages_sent=3,
        messages_unanswered=3
    )

    profile = user.profile
    profile.account_status = 'presumed_deceased'
    profile.death_verification_triggered_at = timezone.now()
    profile.save()

    _notify_admin_death_triggered(user, days_inactive)


def check_expired_verifications():
    from notifications.models import VerificationAttempt

    expired = VerificationAttempt.objects.filter(
        responded=False,
        expires_at__lt=timezone.now()
    ).select_related('user')

    for attempt in expired:
        user = attempt.user

        try:
            if user.profile.is_deceased():
                continue
        except UserProfile.DoesNotExist:
            continue

        unanswered_count = VerificationAttempt.objects.filter(
            user=user,
            responded=False,
            expires_at__lt=timezone.now()
        ).count()

        if unanswered_count >= 2:
            _trigger_death_verification(
                user,
                days_inactive=user.profile.inactivity_threshold_days
            )


def process_death_certificate(user, certificate_file, absher_reference=None):
    verification, created = DeathVerification.objects.get_or_create(
        user=user,
        defaults={
            'trigger_method': 'certificate',
            'status': 'pending',
        }
    )

    verification.death_certificate = certificate_file
    verification.absher_reference = absher_reference
    verification.trigger_method = 'certificate'
    verification.save()

    confirm_death(user, method='certificate')


def confirm_death(user, method='inactivity'):
    profile = user.profile
    profile.account_status = 'confirmed_deceased'
    profile.death_confirmed_at = timezone.now()
    profile.save()

    User.objects.filter(pk=user.pk).update(is_active=False)

    DeathVerification.objects.filter(user=user).update(
        status='confirmed',
        confirmed_at=timezone.now()
    )

    _execute_posthumous_actions(user)
    _notify_all_beneficiaries(user)


def _execute_posthumous_actions(user):
    assets = Asset.objects.filter(
        user=user,
        deleted_at__isnull=True
    )

    for asset in assets:
        if asset.posthumous_action == 'delete':
            asset.deleted_at = timezone.now()
            asset.save()
        elif asset.posthumous_action == 'transfer':
            logger.info(f"Asset ready for transfer: {asset.title}")


def _notify_all_beneficiaries(user):
    beneficiaries = Beneficiary.objects.filter(user=user)

    if not beneficiaries.exists():
        return

    for beneficiary in beneficiaries:
        access_code = secrets.token_hex(4).upper()
        beneficiary.access_code = access_code
        beneficiary.save()

        assigned = AssetBeneficiary.objects.filter(
            beneficiary=beneficiary
        ).select_related('asset')

        assets = [ab.asset for ab in assigned]

        if assets:
            notify_beneficiary(user, beneficiary, assets)


def _notify_admin_death_triggered(user, days_inactive):
    from django.conf import settings

    admins = getattr(settings, 'ADMINS', [])
    if not admins:
        return

    admin_email = admins[0][1]
    base_url = getattr(settings, 'APP_BASE_URL', 'http://localhost:8000')

    dispatch(
        template_code='DEATH_ASSUMED_ADMIN',
        template_data={
            'username': user.username,
            'user_id': user.id,
            'days_inactive': days_inactive,
            'triggered_at': timezone.now().strftime('%Y-%m-%d %H:%M UTC'),
            'admin_url': f"{base_url}/admin/auth/user/{user.id}/",
        },
        recipient={
            'email': admin_email,
            'phone': None,
            'user_id': None,
        },
        channels=['email'],
        user=user,
        recipient_type='admin'
    )