from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from users.models import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Shows UserProfile fields directly inside the User admin page.
    So when you click on a user you see everything in one place.
    """
    model   = UserProfile
    can_delete = False
    verbose_name = 'DLMS Profile'
    fields = [
        'phone',
        'national_id',
        'account_status',
        'inactivity_threshold_days',
        'death_verification_triggered_at',
        'death_confirmed_at',
    ]
    readonly_fields = [
        'death_verification_triggered_at',
        'death_confirmed_at',
    ]


class CustomUserAdmin(UserAdmin):
    """
    Extends Django's default User admin with DLMS profile info.
    """
    inlines      = [UserProfileInline]
    list_display = [
        'username',
        'email',
        'get_account_status',
        'last_login',
        'date_joined',
        'is_active',
    ]
    list_filter  = [
        'is_active',
        'profile__account_status',
    ]
    search_fields = ['username', 'email']

    def get_account_status(self, obj):
        try:
            return obj.profile.account_status
        except UserProfile.DoesNotExist:
            return 'No Profile'
    get_account_status.short_description = 'DLMS Status'


# Unregister default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)