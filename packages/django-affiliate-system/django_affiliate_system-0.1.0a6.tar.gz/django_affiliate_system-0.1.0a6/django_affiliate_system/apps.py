from django.apps import AppConfig
from django.conf import settings


class DjangoAffiliateSystemConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_affiliate_system"
    verbose_name = "Django Affiliate System"

    def ready(self):
        """Initialize app when Django starts"""
        # Import signals
        from . import signals  # noqa

        # Validate settings
        self.validate_settings()

    def validate_settings(self):
        """Validate and set default configuration"""
        from .config import get_config, validate_config

        try:
            # This will validate required settings
            validate_config()

            # Ensure settings are accessible
            config = get_config()

            # Set on settings for easy access
            settings.AFFILIATE_SYSTEM = config

        except ValueError as e:
            import warnings

            warnings.warn(
                f"Django Affiliate System configuration error: {e}. "
                "Using defaults for development. "
                "Please configure AFFILIATE_SYSTEM in settings.py for production.",
                RuntimeWarning,
            )
