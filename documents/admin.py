from django.contrib import admin
from documents.models import (
    Asset,
    Beneficiary,
    AssetBeneficiary,
    DeathVerification
)


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display  = [
        'title',
        'asset_type',
        'get_username',
        'privacy_level',
        'sensitivity_level',
        'nlp_score',
        'posthumous_action',
        'created_at',
    ]
    list_filter   = [
        'asset_type',
        'privacy_level',
        'sensitivity_level',
        'posthumous_action',
        'nlp_analyzed',
    ]
    search_fields = ['title', 'user__username']
    readonly_fields = [
        'asset_id',
        'nlp_score',
        'nlp_analyzed',
        'sensitivity_level',
        'created_at',
        'updated_at',
    ]
    ordering = ['-created_at']

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Owner'


class AssetBeneficiaryInline(admin.TabularInline):
    """Shows assigned assets directly inside Beneficiary page."""
    model      = AssetBeneficiary
    extra      = 0
    readonly_fields = ['assigned_at']


@admin.register(Beneficiary)
class BeneficiaryAdmin(admin.ModelAdmin):
    list_display  = [
        'name',
        'relationship',
        'get_username',
        'has_accessed',
        'created_at',
    ]
    list_filter   = ['relationship', 'has_accessed']
    search_fields = ['user__username']
    readonly_fields = ['access_code', 'created_at']
    inlines       = [AssetBeneficiaryInline]
    ordering      = ['-created_at']

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'User'


@admin.register(DeathVerification)
class DeathVerificationAdmin(admin.ModelAdmin):
    list_display  = [
        'get_username',
        'trigger_method',
        'status',
        'messages_sent',
        'messages_unanswered',
        'triggered_at',
        'confirmed_at',
    ]
    list_filter   = ['status', 'trigger_method']
    search_fields = ['user__username']
    readonly_fields = [
        'triggered_at',
        'confirmed_at',
        'cancelled_at',
    ]
    ordering = ['-triggered_at']

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'User'

    # Add confirm death action in admin
    actions = ['confirm_death_action']

    def confirm_death_action(self, request, queryset):
        from documents.death_verification import confirm_death
        for verification in queryset:
            if verification.status == 'pending':
                confirm_death(
                    verification.user,
                    method='admin'
                )
        self.message_user(
            request,
            f"Death confirmed for {queryset.count()} user(s)."
        )
    confirm_death_action.short_description = "Confirm death for selected users"
