# tasks.py
import time

from django.utils import timezone

try:
    from celery import shared_task

    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

    # Fallback decorator if Celery isn't installed
    def shared_task(func):
        return func


from .models import Commission, Payout


@shared_task
def process_payout(payout_id):
    """
    Mock payout processing task.
    Simulates payment through Stripe/PayPal and updates commissions.
    """
    if not CELERY_AVAILABLE:
        raise ImportError("Celery is required for async tasks")

    payout = Payout.objects.get(id=payout_id)

    if payout.status != "pending":
        return

    payout.status = "processing"
    payout.save()

    # Simulate processing delay (mock API call)
    time.sleep(5)

    try:
        # Mock successful payment
        payout.status = "paid"
        payout.processed_at = timezone.now()
        payout.reference = f"mock_pay_{payout.id}"
        payout.save()

        # Mark all approved commissions as paid
        Commission.objects.filter(affiliate=payout.affiliate, status="approved").update(
            status="paid"
        )

    except Exception as e:
        payout.status = "failed"
        payout.metadata["error"] = str(e)
        payout.save()
