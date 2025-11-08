"""Models for django-temp-permissions.

This module provides models for managing temporary permissions in Django,
allowing administrators to grant time-limited permissions to users.
"""

from django.contrib.auth.models import Permission
from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

from django_temp_permissions.validators import validate_date_not_in_past

User = get_user_model()  # noqa


class BaseTemporaryPermission(models.Model):
    """Abstract base model for temporary permissions.

    Provides common fields for all temporary permission types including
    time constraints and optional notes.

    Attributes:
        start_datetime: When the temporary permission becomes active
        end_datetime: When the temporary permission expires
        notes: Optional notes about why the permission was granted

    """

    permissions = models.ManyToManyField(
        Permission, related_name="temporary_permissions", help_text=_("The permission being granted temporarily")
    )

    start_datetime = models.DateTimeField(
        validators=[validate_date_not_in_past], help_text=_("Date and time when the permission becomes active")
    )
    end_datetime = models.DateTimeField(
        validators=[validate_date_not_in_past], help_text=_("Date and time when the permission expires")
    )
    notes = models.TextField(blank=True, default="", help_text=_("Optional notes about this temporary permission"))

    class Meta:
        abstract = True


class TemporaryPermissionQuerySet(models.QuerySet):
    """Custom chained queryset for TemporaryPermission."""

    def get_active_permissions(self, user: User) -> QuerySet[Permission]:
        """Permissions granted to a given user."""
        now = timezone.now()
        return Permission.objects.filter(
            temporary_permissions__user=user,
            temporary_permissions__start_datetime__lte=now,
            temporary_permissions__end_datetime__gt=now,
        ).distinct()

    def with_perm(self, permission: Permission | str, content_type_app_label: str | None = None) -> QuerySet[User]:
        """Query for users whose permission is currently active.

        Active means the current time (to the second) lies within
        the start and end datetime specified within the TemporaryPermission
        linked to the permission.

        Args:
            permission: The Django permission being granted temporarily.
            content_type_app_label: The Django content type app label.

        Returns:
            A QuerySet of user(s).

        """
        if isinstance(permission, str):
            permission = Permission.objects.get(content_type__app_label=content_type_app_label, codename=permission)

        now = timezone.now()
        return User.objects.filter(
            temporary_permissions__permissions=permission,
            temporary_permissions__start_datetime__lte=now,
            temporary_permissions__end_datetime__gt=now,
        ).distinct()

    def overlapping(self, temp_perm: 'TemporaryPermission') -> QuerySet['TemporaryPermission']:
        """Find overlapping temporary permissions for the same user, for the same time period.

        Args:
            temp_perm: Either a TempPerm instance or an integer ID

        Returns:
            A QuerySet of TemporaryPermission(s).

        """
        if isinstance(temp_perm, int):
            temp_perm = self.get(id=temp_perm)

        # Get the permission IDs from temp_perm
        permission_ids = temp_perm.permissions.values_list("id", flat=True)

        return (
            self.filter(
                user=temp_perm.user,
                start_datetime__lte=temp_perm.end_datetime,
                end_datetime__gte=temp_perm.start_datetime,
                permissions__id__in=permission_ids,
            )
            .exclude(id=temp_perm.id)
            .distinct()
        )


class TemporaryPermission(BaseTemporaryPermission):
    """Temporary permission granted to a specific user.

    Links a user to a permission with time constraints.
    """

    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="temporary_permissions",
        help_text=_("User receiving the temporary permission"),
    )

    objects = TemporaryPermissionQuerySet().as_manager()

    def __str__(self) -> str:
        """Human-readable representation of the temporary permission."""
        return f"{self.user}: {self.start_datetime} → {self.end_datetime}"

    def clean(self) -> None:
        """Validate temporary permission constraints.

        Additional validations:
        - Validate that at least one permission is assigned.
        - Validate that end_datetime is after start_datetime.
        """
        if self.pk and not self.permissions.exists():
            raise ValidationError(_("At least one Permission must be selected."))

        # Preventing an exception in case of either not being passed
        if self.start_datetime and self.end_datetime and self.end_datetime <= self.start_datetime:
            raise ValidationError(_("End datetime must be after start datetime."))

        super().clean()
