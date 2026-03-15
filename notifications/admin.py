from django.contrib import admin
from notifications.models import Notification, VerificationAttempt


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = [
        'template_code',
        'channel',
        'recipient_type',
        'status',
        'get_username',
        'created_at',
        'sent_at',
    ]
    list_filter   = ['channel', 'status', 'recipient_type', 'template_code']
    search_fields = ['template_code', 'user__username']
    readonly_fields = ['created_at', 'sent_at']
    ordering      = ['-created_at']

    def get_username(self, obj):
        if obj.user:
            return obj.user.username
        return 'N/A'
    get_username.short_description = 'User'


@admin.register(VerificationAttempt)
class VerificationAttemptAdmin(admin.ModelAdmin):
    list_display  = [
        'get_username',
        'responded',
        'created_at',
        'expires_at',
        'is_expired',
    ]
    list_filter   = ['responded']
    search_fields = ['user__username']
    readonly_fields = ['token', 'created_at', 'expires_at']
    ordering      = ['-created_at']

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'User'

    def is_expired(self, obj):
        from django.utils import timezone
        return timezone.now() > obj.expires_at
    is_expired.boolean = True
    is_expired.short_description = 'Expired?'