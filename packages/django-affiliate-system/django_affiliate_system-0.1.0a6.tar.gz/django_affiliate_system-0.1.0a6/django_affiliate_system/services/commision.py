# services/commissions.py

from decimal import Decimal
from django.db import transaction
from django.utils import timezone

from django_affiliate_system.models import Commission, CommissionRule


def create_commission(action):
    """
    Calculate and create commission for a converted action.

    Args:
        action: ReferralAction instance that has been converted

    Returns:
        Commission instance or None if no applicable rule found
    """
    # CHANGED: Get affiliate directly from action
    affiliate = action.affiliate

    # CHANGED: Get tenant through affiliate relationship
    tenant = affiliate.tenant

    # Find applicable commission rule
    # First try tenant-specific rule, then fall back to global rule
    rule = None

    # Try tenant-specific rule for this action type
    if tenant:
        rule = (
            CommissionRule.objects.filter(
                tenant=tenant, action_type=action.action_type, is_active=True
            )
            .order_by("-priority")
            .first()
        )

    # Fall back to tenant-specific "other" rule
    if not rule and tenant:
        rule = (
            CommissionRule.objects.filter(tenant=tenant, action_type="other", is_active=True)
            .order_by("-priority")
            .first()
        )

    # Fall back to global rule for this action type
    if not rule:
        rule = (
            CommissionRule.objects.filter(
                tenant__isnull=True, action_type=action.action_type, is_active=True
            )
            .order_by("-priority")
            .first()
        )

    # Fall back to global "other" rule
    if not rule:
        rule = (
            CommissionRule.objects.filter(tenant__isnull=True, action_type="other", is_active=True)
            .order_by("-priority")
            .first()
        )

    if not rule:
        # No applicable rule found
        return None

    print("conversion value!!!!!!!:", action.conversion_value)

    # Calculate commission amount
    if rule.is_percentage:
        print("Percentage-based commission rule applied", rule.value)
        # Percentage-based commission
        amount = (Decimal(action.conversion_value) or 0) * (rule.value / 100)

        # Apply min/max limits
        if rule.min_value is not None:
            amount = max(amount, rule.min_value)
        if rule.max_value is not None:
            amount = min(amount, rule.max_value)

        rate = rule.value
    else:
        print("Flat amount commission rule applied")
        # Flat amount commission
        amount = rule.value
        rate = 0  # Rate is 0 for flat commissions

    # Create commission and update affiliate balance atomically
    with transaction.atomic():
        commission = Commission.objects.create(
            affiliate=affiliate,
            referral_action=action,
            amount=amount,
            rate=rate,
            status="pending",
        )

        # Update affiliate balance
        affiliate.balance += amount
        affiliate.save(update_fields=["balance"])

    return commission


def create_attributed_commission(action, session):
    """
    Create commission based on attribution model.

    For session-based tracking, determines which link/affiliate gets credit
    based on first-click or last-click attribution.

    Args:
        action: ReferralAction instance
        session: ReferralSession instance

    Returns:
        Commission instance or None
    """
    attribution_model = action.metadata.get("attribution_model", "last_click")

    if attribution_model == "first_click":
        attributed_affiliate = session.first_referral_link.affiliate
        attributed_link = session.first_referral_link
    else:  # last_click (default)
        attributed_affiliate = session.last_referral_link.affiliate
        attributed_link = session.last_referral_link

    # Update action with attributed affiliate/link
    # This allows the commission to be correctly attributed
    action.affiliate = attributed_affiliate
    action.referral_link = attributed_link
    action.save(update_fields=["affiliate", "referral_link"])

    # Create commission using the standard flow
    return create_commission(action)


def calculate_commission_preview(affiliate, action_type, conversion_value):
    """
    Preview what commission would be earned without creating it.
    Useful for showing potential earnings to affiliates.

    Args:
        affiliate: Affiliate instance
        action_type: Type of action (e.g., 'purchase', 'signup')
        conversion_value: Value of the conversion

    Returns:
        dict with commission details or None
    """
    tenant = affiliate.tenant

    # Find applicable rule (same logic as create_commission)
    rule = None

    if tenant:
        rule = (
            CommissionRule.objects.filter(tenant=tenant, action_type=action_type, is_active=True)
            .order_by("-priority")
            .first()
        )

    if not rule and tenant:
        rule = (
            CommissionRule.objects.filter(tenant=tenant, action_type="other", is_active=True)
            .order_by("-priority")
            .first()
        )

    if not rule:
        rule = (
            CommissionRule.objects.filter(
                tenant__isnull=True, action_type=action_type, is_active=True
            )
            .order_by("-priority")
            .first()
        )

    if not rule:
        rule = (
            CommissionRule.objects.filter(tenant__isnull=True, action_type="other", is_active=True)
            .order_by("-priority")
            .first()
        )

    if not rule:
        return None

    # Calculate amount
    if rule.is_percentage:
        amount = (conversion_value or 0) * (rule.value / 100)
        if rule.min_value is not None:
            amount = max(amount, rule.min_value)
        if rule.max_value is not None:
            amount = min(amount, rule.max_value)
    else:
        amount = rule.value

    return {
        "amount": float(amount),
        "rate": float(rule.value) if rule.is_percentage else 0,
        "is_percentage": rule.is_percentage,
        "rule_name": rule.name,
        "conversion_value": float(conversion_value or 0),
    }


def bulk_approve_commissions(commission_ids, approved_by=None):
    """
    Approve multiple pending commissions at once.

    Args:
        commission_ids: List of commission IDs to approve
        approved_by: User who approved (optional, for audit trail)

    Returns:
        int: Number of commissions approved
    """
    with transaction.atomic():
        updated = Commission.objects.filter(id__in=commission_ids, status="pending").update(
            status="approved",
            # You might want to add approved_at and approved_by fields
        )

    return updated


def reject_commission(commission_id, reason=None):
    """
    Reject a commission and reverse the balance update.

    Args:
        commission_id: Commission ID to reject
        reason: Reason for rejection (optional)

    Returns:
        Commission instance or None
    """
    try:
        commission = Commission.objects.get(id=commission_id)

        if commission.status != "pending":
            raise ValueError(f"Cannot reject commission with status: {commission.status}")

        with transaction.atomic():
            # Reverse the balance
            affiliate = commission.affiliate
            affiliate.balance -= commission.amount
            affiliate.save(update_fields=["balance"])

            # Update commission status
            commission.status = "rejected"
            if reason:
                # You might want to add a rejection_reason field
                if not commission.referral_action.metadata:
                    commission.referral_action.metadata = {}
                commission.referral_action.metadata["rejection_reason"] = reason
                commission.referral_action.save(update_fields=["metadata"])
            commission.save(update_fields=["status"])

        return commission

    except Commission.DoesNotExist:
        return None


def get_commission_summary(affiliate, start_date=None, end_date=None):
    """
    Get commission summary for an affiliate.

    Args:
        affiliate: Affiliate instance
        start_date: Optional start date filter
        end_date: Optional end date filter

    Returns:
        dict with commission summary
    """
    from django.db.models import Sum, Count, Avg

    queryset = Commission.objects.filter(affiliate=affiliate)

    if start_date:
        queryset = queryset.filter(calculated_at__gte=start_date)
    if end_date:
        queryset = queryset.filter(calculated_at__lte=end_date)

    summary = queryset.aggregate(
        total_commissions=Count("id"),
        total_amount=Sum("amount"),
        pending_amount=Sum("amount", filter=Q(status="pending")),
        approved_amount=Sum("amount", filter=Q(status="approved")),
        paid_amount=Sum("amount", filter=Q(status="paid")),
        rejected_amount=Sum("amount", filter=Q(status="rejected")),
        average_commission=Avg("amount"),
    )

    # Convert Decimals to floats
    return {key: float(value) if value is not None else 0 for key, value in summary.items()}
