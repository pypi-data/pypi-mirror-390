import re

from django.conf import settings
from rest_framework import serializers

from .config import get_config
from .models import (
    Affiliate,
    Commission,
    CommissionRule,
    Payout,
    ReferralAction,
    ReferralLink,
    Tenant,
)


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = [
            "id",
            "name",
            "slug",
            "subdomain",
            "destination_url",
            "created_at",
            "default_commission_rate",
            "cookie_duration_days",
            "is_active",
        ]
        read_only_fields = ["created_at", "owner"]


class AffiliateSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source="user.email", read_only=True)
    tenant_name = serializers.CharField(source="tenant.name", read_only=True, allow_null=True)

    class Meta:
        model = Affiliate
        fields = [
            "id",
            "tenant",
            "tenant_name",
            "user",
            "user_email",
            "code",
            "is_active",
            "balance",
            "payout_threshold",
            "payout_method",
            "joined_at",
        ]
        read_only_fields = ["code", "balance", "user", "tenant", "joined_at"]


class ReferralLinkSerializer(serializers.ModelSerializer):
    full_url = serializers.SerializerMethodField()
    affiliate_code = serializers.CharField(source="affiliate.code", read_only=True)

    # Statistics (optional - can be expensive)
    total_clicks = serializers.SerializerMethodField()
    total_conversions = serializers.SerializerMethodField()
    conversion_rate = serializers.SerializerMethodField()

    class Meta:
        model = ReferralLink
        fields = [
            "id",
            "affiliate",
            "affiliate_code",
            "slug",
            "destination_url",
            "full_url",
            "campaign_name",
            "notes",
            "is_active",
            "created_at",
            "total_clicks",
            "total_conversions",
            "conversion_rate",
        ]
        read_only_fields = ["created_at", "affiliate"]

    def get_full_url(self, obj):
        """Generate full referral URL"""
        config = get_config()
        protocol = config.get("DOMAIN_PROTOCOL", "https")
        domain = config.get("DOMAIN", "localhost:8000")
        return f"{protocol}://{domain}/?ref={obj.slug}"

    def _get_actions(self, obj):
        """Helper to get actions for stats (with caching)"""
        if not hasattr(self, "_actions_cache"):
            self._actions_cache = {}

        if obj.id not in self._actions_cache:
            # Get date range from context if provided
            request = self.context.get("request")
            queryset = ReferralAction.objects.filter(referral_link=obj)

            if request and (start_date := request.query_params.get("start_date")):
                end_date = request.query_params.get("end_date")
                if end_date:
                    queryset = queryset.filter(timestamp__range=[start_date, end_date])

            self._actions_cache[obj.id] = queryset

        return self._actions_cache[obj.id]

    def get_total_clicks(self, obj):
        return self._get_actions(obj).filter(action_type="click").count()

    def get_total_conversions(self, obj):
        return self._get_actions(obj).filter(is_converted=True).count()

    def get_conversion_rate(self, obj):
        clicks = self.get_total_clicks(obj)
        conversions = self.get_total_conversions(obj)
        return round((conversions / clicks * 100), 2) if clicks > 0 else 0

    def validate_slug(self, value):
        """
        Validate slug format and uniqueness.
        Allows letters, numbers, and hyphens.
        """
        instance = getattr(self, "instance", None)

        # If updating and slug hasn't changed, skip validation
        if instance and instance.slug == value:
            return value

        # Validate format (alphanumeric and hyphens only)
        if not re.match(r"^[A-Za-z0-9-]+$", value):
            raise serializers.ValidationError("Slug can only contain letters, numbers, and hyphens")

        # Check length
        if len(value) < 3:
            raise serializers.ValidationError("Slug must be at least 3 characters long")

        # Check uniqueness (globally unique)
        if (
            ReferralLink.objects.filter(slug=value)
            .exclude(pk=getattr(instance, "pk", None))
            .exists()
        ):
            raise serializers.ValidationError("This slug is already in use")

        return value

    def validate_destination_url(self, value):
        """Validate destination URL format"""
        if not value.startswith(("http://", "https://")):
            raise serializers.ValidationError("Destination URL must start with http:// or https://")
        return value


class ReferralActionSerializer(serializers.ModelSerializer):
    affiliate_code = serializers.CharField(source="affiliate.code", read_only=True)
    affiliate_email = serializers.EmailField(source="affiliate.user.email", read_only=True)
    referral_link_slug = serializers.CharField(source="referral_link.slug", read_only=True)
    affiliate_code = serializers.CharField(source="referral_link.affiliate.code", read_only=True)
    tracking_method = serializers.SerializerMethodField()

    class Meta:
        model = ReferralAction
        fields = [
            "id",
            "affiliate",
            "affiliate_code",
            "affiliate_email",
            "referral_link",
            "referral_link_slug",
            "action_type",
            "tracking_method",
            "ip_address",
            "user_agent",
            "referring_url",
            "timestamp",
            "metadata",
            "converted_at",
            "conversion_value",
            "is_converted",
            "session_id",
        ]
        read_only_fields = ["id", "timestamp", "affiliate", "referral_link"]

    def get_tracking_method(self, obj):
        return "link" if obj.referral_link else "code"


class CommissionSerializer(serializers.ModelSerializer):
    affiliate_code = serializers.CharField(source="affiliate.code", read_only=True)
    action_type = serializers.CharField(source="referral_action.action_type", read_only=True)

    class Meta:
        model = Commission
        fields = [
            "id",
            "affiliate",
            "affiliate_code",
            "referral_action",
            "action_type",
            "amount",
            "rate",
            "calculated_at",
            "status",
        ]
        read_only_fields = ["amount", "rate", "calculated_at", "affiliate"]


class PayoutSerializer(serializers.ModelSerializer):
    affiliate_code = serializers.CharField(source="affiliate.code", read_only=True)

    class Meta:
        model = Payout
        fields = [
            "id",
            "tenant",
            "affiliate",
            "affiliate_code",
            "amount",
            "status",
            "created_at",
            "processed_at",
            "method",
            "reference",
        ]
        read_only_fields = [
            "tenant",
            "created_at",
            "processed_at",
            "reference",
            "affiliate",
        ]


class CommissionRuleSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source="tenant.name", read_only=True, allow_null=True)

    class Meta:
        model = CommissionRule
        fields = [
            "id",
            "tenant",
            "tenant_name",
            "name",
            "action_type",
            "is_percentage",
            "value",
            "min_value",
            "max_value",
            "is_active",
            "priority",
        ]
        read_only_fields = ["tenant"]

    def validate(self, data):
        """Validate commission rule values"""
        if data.get("is_percentage"):
            value = data.get("value", 0)
            if value < 0 or value > 100:
                raise serializers.ValidationError("Percentage value must be between 0 and 100")

            # Validate min/max if provided
            min_val = data.get("min_value")
            max_val = data.get("max_value")

            if min_val is not None and max_val is not None:
                if min_val > max_val:
                    raise serializers.ValidationError("min_value cannot be greater than max_value")

        return data


class TrackingEventSerializer(serializers.Serializer):
    """Serializer for tracking endpoint requests"""

    referral_code = serializers.CharField(required=False, allow_blank=True)
    referral_slug = serializers.CharField(required=False, allow_blank=True)
    event_type = serializers.CharField(default="click")
    conversion_value = serializers.DecimalField(
        max_digits=10, decimal_places=2, required=False, default=0
    )
    is_conversion = serializers.BooleanField(default=False)
    session_id = serializers.CharField(required=False, allow_blank=True)
    use_sessions = serializers.BooleanField(default=False)
    attribution_model = serializers.CharField(default="last_click")
    metadata = serializers.JSONField(required=False, default=dict)

    def validate(self, data):
        """Ensure either referral_code or referral_slug is provided"""
        if not data.get("referral_code") and not data.get("referral_slug"):
            raise serializers.ValidationError("Either referral_code or referral_slug is required")
        return data
