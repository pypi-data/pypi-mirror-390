import enum

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


def get_affiliate_config():
    """Helper to get affiliate system configuration"""
    return getattr(settings, "AFFILIATE_SYSTEM", {})


class Tenant(models.Model):
    """Optional multi-tenant support for platforms using the affiliate system"""

    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    subdomain = models.CharField(max_length=255, blank=True, unique=True, null=True)
    destination_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_tenants",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)

    # Commission settings (can override defaults)
    default_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=10.0, help_text="Default commission rate percentage"
    )
    cookie_duration_days = models.PositiveIntegerField(
        default=30, help_text="How long to track referrals via cookies"
    )

    class Meta:
        db_table = "affiliates_tenant"

    def __str__(self):
        return self.name


class Affiliate(models.Model):
    """Users who refer others"""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="affiliates",
        null=True,
        blank=True,
        help_text="Optional: Associate affiliate with a specific tenant",
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="affiliates")
    code = models.CharField(max_length=50, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    balance = models.DecimalField(
        max_digits=10, decimal_places=2, default=0.0, help_text="Current unpaid commission balance"
    )

    # Payout settings
    payout_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50.0,
        help_text="Minimum balance required to request payout",
    )
    payout_method = models.CharField(
        max_length=50, blank=True, help_text="e.g., stripe, paypal, bank_transfer"
    )
    payout_details = models.JSONField(
        default=dict, help_text="Payment method details (encrypted in production)"
    )

    class Meta:
        db_table = "affiliates_affiliate"
        unique_together = [("tenant", "user")]
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["user", "is_active"]),
        ]

    def __str__(self):
        if self.tenant:
            return f"{self.user.email} ({self.tenant})"
        return f"{self.user.email} - {self.code}"


class ReferralLink(models.Model):
    """Unique referral links for affiliates"""

    affiliate = models.ForeignKey(
        Affiliate, on_delete=models.CASCADE, related_name="referral_links"
    )
    slug = models.SlugField(unique=True, db_index=True)
    destination_url = models.URLField(help_text="Where to redirect users who click this link")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Optional metadata
    campaign_name = models.CharField(
        max_length=255, blank=True, help_text="Optional campaign identifier"
    )
    notes = models.TextField(blank=True, help_text="Internal notes about this link")

    class Meta:
        db_table = "affiliates_referrallink"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["affiliate", "is_active"]),
        ]

    def __str__(self):
        return f"{self.slug} -> {self.destination_url}"


class ReferralActionType(enum.Enum):
    CLICK = "click"
    PAGE_VIEW = "page_view"
    SIGNUP = "signup"
    PURCHASE = "purchase"
    OTHER = "other"


class ReferralAction(models.Model):
    """Track all referral actions (clicks, signups, purchases)"""

    affiliate = models.ForeignKey(
        Affiliate,
        on_delete=models.CASCADE,
        related_name="actions",
        help_text="Affiliate who gets credit for this action",
    )
    referral_link = models.ForeignKey(
        ReferralLink,
        on_delete=models.CASCADE,
        related_name="actions",
        null=True,
        blank=True,
        help_text="Optional: Specific campaign link used",
    )
    action_type = models.CharField(
        max_length=20, choices=[(tag.value, tag.name) for tag in ReferralActionType]
    )

    # Tracking data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referring_url = models.URLField(blank=True, max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    metadata = models.JSONField(
        default=dict, help_text="Additional tracking data (UTM params, device info, etc.)"
    )

    # Conversion tracking
    converted_at = models.DateTimeField(null=True, blank=True)
    conversion_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Monetary value of the conversion",
    )
    is_converted = models.BooleanField(default=False, db_index=True)
    session_id = models.CharField(
        max_length=100, blank=True, help_text="Optional session ID for multi-touch attribution"
    )

    class Meta:
        db_table = "affiliates_referralaction"
        indexes = [
            models.Index(fields=["affiliate", "action_type"]),
            models.Index(fields=["affiliate", "is_converted"]),
            models.Index(fields=["referral_link", "action_type"]),
            models.Index(fields=["is_converted"]),
            models.Index(fields=["timestamp"]),
            models.Index(fields=["session_id"]),
        ]

    def __str__(self):
        if self.referral_link:
            return f"{self.action_type} via {self.referral_link.slug} ({self.affiliate.code})"
        return f"{self.action_type} via code {self.affiliate.code}"

    @property
    def tenant(self):
        """Helper property to access tenant through relationship"""
        return self.affiliate.tenant


class Commission(models.Model):
    """Commissions earned from referrals"""

    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name="commissions")
    referral_action = models.OneToOneField(
        ReferralAction, on_delete=models.CASCADE, related_name="commission"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Commission rate at time of action (if percentage-based)",
    )
    calculated_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("paid", "Paid"),
        ],
        default="pending",
        db_index=True,
    )

    class Meta:
        db_table = "affiliates_commission"
        indexes = [
            models.Index(fields=["affiliate", "status"]),
            models.Index(fields=["calculated_at"]),
        ]

    def __str__(self):
        return f"${self.amount} for {self.affiliate.code}"


class Payout(models.Model):
    """Payments to affiliates"""

    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name="payouts", null=True, blank=True
    )
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE, related_name="payouts")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("processing", "Processing"),
            ("paid", "Paid"),
            ("failed", "Failed"),
        ],
        default="pending",
        db_index=True,
    )
    method = models.CharField(max_length=50)
    reference = models.CharField(
        max_length=255, blank=True, help_text="External payment reference ID"
    )
    metadata = models.JSONField(default=dict)

    class Meta:
        db_table = "affiliates_payout"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["affiliate", "status"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        return f"Payout #{self.id} - ${self.amount} to {self.affiliate.code}"


class CommissionRule(models.Model):
    """Rules for calculating commissions"""

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="commission_rules",
        null=True,
        blank=True,
        help_text="Optional: Tenant-specific rules. Leave blank for global rules.",
    )
    name = models.CharField(max_length=255)
    action_type = models.CharField(
        max_length=20, choices=[(tag.value, tag.name) for tag in ReferralActionType]
    )
    is_percentage = models.BooleanField(
        default=True, help_text="True for percentage-based, False for flat amount"
    )
    value = models.DecimalField(
        max_digits=10, decimal_places=2, help_text="Percentage (e.g., 10.00 for 10%) or flat amount"
    )
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Minimum commission amount (for percentage-based)",
    )
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum commission amount (for percentage-based)",
    )
    is_active = models.BooleanField(default=True)
    priority = models.PositiveIntegerField(
        default=0, help_text="Higher priority rules are evaluated first"
    )

    class Meta:
        db_table = "affiliates_commissionrule"
        ordering = ["-priority", "id"]
        indexes = [
            models.Index(fields=["tenant", "action_type", "is_active"]),
        ]

    def __str__(self):
        tenant_info = f" ({self.tenant})" if self.tenant else " (Global)"
        return f"{self.name}{tenant_info}"


class ReferralSession(models.Model):
    """Track user sessions across multiple touchpoints for attribution"""

    session_id = models.CharField(max_length=100, unique=True, db_index=True)
    affiliate = models.ForeignKey(Affiliate, on_delete=models.CASCADE)
    first_referral_link = models.ForeignKey(
        ReferralLink, on_delete=models.CASCADE, related_name="first_sessions"
    )
    last_referral_link = models.ForeignKey(
        ReferralLink, on_delete=models.CASCADE, related_name="last_sessions"
    )
    first_touch = models.DateTimeField(auto_now_add=True)
    last_touch = models.DateTimeField(auto_now=True)
    is_converted = models.BooleanField(default=False, db_index=True)
    conversion_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = "affiliates_referralsession"
        indexes = [
            models.Index(fields=["session_id"]),
            models.Index(fields=["affiliate", "is_converted"]),
        ]

    def __str__(self):
        return f"Session {self.session_id} - {self.affiliate.code}"
