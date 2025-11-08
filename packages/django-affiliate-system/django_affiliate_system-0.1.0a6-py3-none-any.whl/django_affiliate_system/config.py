"""
Django Affiliate System Configuration

Add this to your Django settings.py:

AFFILIATE_SYSTEM = {
    # Domain configuration
    'DOMAIN_PROTOCOL': 'https',  # or 'http' for local development
    'DOMAIN': 'yourdomain.com',  # Your main domain

    # Tracking configuration
    'DEFAULT_COMMISSION_RATE': 10.0,  # Default percentage
    'COOKIE_DURATION_DAYS': 30,  # How long to track referrals

    # Redirect configuration
    'DEFAULT_REDIRECT_URL': '/',  # Where to redirect invalid referral links

    # CORS (if using tracking from different domains)
    'ALLOWED_CORS_ORIGINS': [
        'https://yourdomain.com',
        'https://www.yourdomain.com',
    ],

    # Features
    'ENABLE_MULTI_TENANCY': False,  # Set to True to enable tenant isolation
    'ENABLE_SESSIONS': False,  # Set to True for multi-touch attribution
    'DEFAULT_ATTRIBUTION_MODEL': 'last_click',  # or 'first_click', 'linear'

    # Payout configuration
    'DEFAULT_PAYOUT_THRESHOLD': 50.0,  # Minimum balance for payout
    'PAYOUT_METHODS': ['stripe', 'paypal', 'bank_transfer'],

    # Commission rules
    'AUTO_APPROVE_COMMISSIONS': False,  # Auto-approve or require manual approval
}

# Optional: Configure JWT if not already set
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    # ... other DRF settings
}
"""

from django.conf import settings


def get_config():
    """Get affiliate system configuration with defaults"""
    defaults = {
        "DOMAIN_PROTOCOL": "https",
        "DOMAIN": "localhost:8000",
        "DEFAULT_COMMISSION_RATE": 10.0,
        "COOKIE_DURATION_DAYS": 30,
        "DEFAULT_REDIRECT_URL": "/",
        "ALLOWED_CORS_ORIGINS": [],
        "ENABLE_MULTI_TENANCY": False,
        "ENABLE_SESSIONS": False,
        "DEFAULT_ATTRIBUTION_MODEL": "last_click",
        "DEFAULT_PAYOUT_THRESHOLD": 50.0,
        "PAYOUT_METHODS": ["stripe", "paypal", "bank_transfer"],
        "AUTO_APPROVE_COMMISSIONS": False,
    }

    config = getattr(settings, "AFFILIATE_SYSTEM", {})

    # Merge with defaults
    for key, default_value in defaults.items():
        if key not in config:
            config[key] = default_value

    return config


# Validate configuration on import
def validate_config():
    """Validate configuration and raise errors if invalid"""
    config = get_config()

    required_keys = ["DOMAIN_PROTOCOL", "DOMAIN"]
    for key in required_keys:
        if not config.get(key):
            raise ValueError(f"AFFILIATE_SYSTEM['{key}'] is required in settings.py")

    if config["DOMAIN_PROTOCOL"] not in ["http", "https"]:
        raise ValueError("AFFILIATE_SYSTEM['DOMAIN_PROTOCOL'] must be 'http' or 'https'")
