# signals.py
import logging

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .config import get_config
from .models import Affiliate, ReferralAction, Tenant

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def track_referred_signup(sender, instance, created, **kwargs):
    """
    Track user signups that came from referral links.
    Checks for referral cookies and creates conversion actions.
    """
    if not created:
        return

    # Get request from kwargs if available (set by middleware)
    request = kwargs.get("request")
    if not request:
        logger.debug("No request object available for signup tracking")
        return

    # Check for referral code in request (set by middleware)
    ref_code = getattr(request, "affiliate_ref_code", None)
    if not ref_code:
        logger.debug("No referral code found for new user signup")
        return

    try:
        # Find the affiliate
        affiliate = Affiliate.objects.select_related("tenant").get(code=ref_code, is_active=True)
    except Affiliate.DoesNotExist:
        logger.warning(f"Invalid referral code in cookie: {ref_code}")
        return

    # Get or create a referral link for tracking
    # (We might not know the exact link, so we use the first active one)
    referral_link = affiliate.referral_links.filter(is_active=True).first()

    if not referral_link:
        logger.warning(f"No active referral link found for affiliate {affiliate.code}")
        return

    # Create signup conversion action
    action = ReferralAction.objects.create(
        tenant=affiliate.tenant,
        referral_link=referral_link,
        action_type="signup",
        ip_address=request.META.get("REMOTE_ADDR"),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        converted_at=timezone.now(),
        conversion_value=0,  # Signups might have no immediate value
        is_converted=True,
        metadata={
            "user_id": instance.id,
            "tracked_via": "cookie",
        },
    )

    logger.info(
        f"Tracked signup conversion for user {instance.id} " f"via affiliate {affiliate.code}"
    )

    # Create commission if there's a rule for signups
    from .services.commision import create_commission

    create_commission(action)


@receiver(post_save, sender=Affiliate)
def generate_affiliate_code(sender, instance, created, **kwargs):
    """Generate a unique affiliate code if not provided"""
    if created and not instance.code:
        # Generate code from user email or ID
        base_code = instance.user.email.split("@")[0].upper()
        code = base_code

        # Ensure uniqueness
        counter = 1
        while Affiliate.objects.filter(code=code).exists():
            code = f"{base_code}{counter}"
            counter += 1

        instance.code = code
        instance.save(update_fields=["code"])

        logger.info(f"Generated affiliate code: {code} for user {instance.user.id}")
