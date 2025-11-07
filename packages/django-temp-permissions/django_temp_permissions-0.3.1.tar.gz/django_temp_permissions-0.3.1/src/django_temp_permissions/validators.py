"""django_temp_permissions model validators."""

from datetime import datetime, timedelta

from django.conf import settings
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_date_not_in_past(value: datetime) -> None:
    """Validate that a date is not in the past.

    If required the LENIENCE setting allows the extension
    of the time within the date will still be valid.
    By default, it's 5 minutes.
    """
    lenience = getattr(settings, "PAST_PERMISSIONS_LENIENCE", timedelta(minutes=5))

    if value <= timezone.now() - lenience:
        raise ValidationError(_("{value} date is in the past.").format(value=value))
