from django.utils import timezone
from rest_framework.exceptions import ValidationError

from django_affiliate_system.models import (
    Affiliate,
    ReferralAction,
    ReferralLink,
    ReferralSession,
)
from django_affiliate_system.services.commision import (
    create_attributed_commission,
    create_commission,
)


def resolve_referral(referral_code=None, referral_slug=None):
    """
    Resolve referral tracking to affiliate and optional link.

    Returns: tuple (affiliate, referral_link or None)

    - If referral_code provided: Returns (affiliate, None) - direct code tracking
    - If referral_slug provided: Returns (affiliate, link) - campaign tracking

    Raises: ValidationError if not found or invalid
    """
    if referral_code:
        try:
            affiliate = Affiliate.objects.get(code=referral_code, is_active=True)
            return affiliate, None  # Track by code, no specific campaign
        except Affiliate.DoesNotExist:
            raise ValidationError("Invalid referral code")

    elif referral_slug:
        try:
            link = ReferralLink.objects.select_related("affiliate").get(
                slug=referral_slug, is_active=True
            )
            if not link.affiliate.is_active:
                raise ValidationError("Affiliate is not active")
            return link.affiliate, link  # Track specific campaign
        except ReferralLink.DoesNotExist:
            raise ValidationError("Invalid referral link")

    else:
        raise ValidationError("Either referral_code or referral_slug is required")


def process_tracking_event(data, meta, use_sessions=False, attribution_model="last_click"):
    """
    Process a tracking event (click, signup, purchase, etc.)

    Args:
        data: Event data including referral_code OR referral_slug
        meta: Request META for IP/user agent
        use_sessions: Whether to use session-based tracking
        attribution_model: 'first_click' or 'last_click'

    Returns: ReferralAction instance
    """
    referral_code = data.get("referral_code")
    referral_slug = data.get("referral_link_slug")
    event_type = data.get("event_type", "click")
    session_id = data.get("session_id")

    # Resolve to affiliate + optional link
    affiliate, referral_link = resolve_referral(referral_code, referral_slug)

    session = None
    session_created = False

    # Session tracking logic
    if use_sessions and session_id:
        # Only create sessions if tracking by link (campaigns)
        if referral_link:
            session, session_created = ReferralSession.objects.get_or_create(
                session_id=session_id,
                defaults={
                    "affiliate": affiliate,
                    "first_referral_link": referral_link,
                    "last_referral_link": referral_link,
                    "ip_address": meta.get("REMOTE_ADDR"),
                    "user_agent": meta.get("HTTP_USER_AGENT", ""),
                },
            )
            if not session_created:
                session.last_referral_link = referral_link
                session.last_touch = timezone.now()
                session.save()

    # Build metadata
    metadata = {
        **data.get("metadata", {}),
        "session_created": session_created if use_sessions else False,
        "attribution_model": attribution_model,
        "tracking_method": "link" if referral_link else "code",  # Track how it was tracked
    }

    # Create action
    action = ReferralAction.objects.create(
        affiliate=affiliate,  # Always set
        referral_link=referral_link,  # May be None for code-based tracking
        action_type=event_type,
        session_id=session_id if use_sessions else "",
        ip_address=meta.get("REMOTE_ADDR"),
        user_agent=meta.get("HTTP_USER_AGENT", ""),
        referring_url=data.get("metadata", {}).get("referrer", ""),
        conversion_value=data.get("conversion_value", 0),
        metadata=metadata,
    )

    # Handle conversions
    if event_type in ["purchase"] or data.get("is_conversion"):
        action.is_converted = True
        action.converted_at = timezone.now()
        action.save()

        if use_sessions and session:
            session.is_converted = True
            session.conversion_value = action.conversion_value
            session.save()

            return create_attributed_commission(action, session)

        create_commission(action)

    return action


# def create_attributed_commission(action, session):
#     """
#     Create commission based on attribution model.

#     For session-based tracking, determines which link/affiliate gets credit
#     based on first-click or last-click attribution.
#     """
#     attribution_model = action.metadata.get("attribution_model", "last_click")

#     if attribution_model == "first_click":
#         affiliate = session.first_referral_link.affiliate
#         referral_link = session.first_referral_link
#     else:  # last_click
#         affiliate = session.last_referral_link.affiliate
#         referral_link = session.last_referral_link

#     # Update action with attributed affiliate/link
#     action.affiliate = affiliate
#     action.referral_link = referral_link
#     action.save(update_fields=["affiliate", "referral_link"])

#     return create_commission(action)
