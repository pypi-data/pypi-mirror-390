"""Admin configuration for django-temp-permissions."""

from __future__ import annotations

import typing
from typing import Any

from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.base_user import AbstractBaseUser
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _

from django_temp_permissions.models import TemporaryPermission
from django_temp_permissions.signals import permission_overlap_detected


if typing.TYPE_CHECKING:
    from django.contrib.auth.base_user import AbstractBaseUser
    from django.http import HttpRequest, HttpResponse

try:
    from admin_extra_buttons.decorators import button
    from admin_extra_buttons.mixins import ExtraButtonsMixin
    from adminfilters.dates import DateRangeFilter
    from adminfilters.mixin import AdminFiltersMixin

    @admin.register(TemporaryPermission)
    class TemporaryPermissionAdmin(ExtraButtonsMixin, AdminFiltersMixin, admin.ModelAdmin):
        """Admin interface for TemporaryPermission model.

        Provides a user-friendly interface for managing temporary permissions
        with filtering, searching, and display customization.
        """

        list_display = [
            "user",
            "start_datetime",
            "end_datetime",
        ]
        search_fields = ("user__username", "user__email")
        ordering = ("-start_datetime",)

        filter_horizontal = ("permissions",)

        list_filter = (
            ("start_datetime", DateRangeFilter),
            ("end_datetime", DateRangeFilter),
        )

        def _check_overlaps(self, request: HttpRequest, user_temp_permission_id: int) -> None:
            """Inform the user via the admin UI that the permission(s) they assigned."""
            temp_perm = TemporaryPermission.objects.get(id=user_temp_permission_id)
            for overlapping_perm in TemporaryPermission.objects.overlapping(temp_perm):
                url = reverse("admin:django_temp_permissions_temporarypermission_change", args=(overlapping_perm.pk,))
                link = format_html(
                    '<a href="{url}" target="_blank"> User Temporary Permission ID {id}</a>',
                    url=url,
                    id=overlapping_perm.id,
                )

                message = format_html(
                    _(
                        "One or more of the permissions you saved are already covered for the specified time period in:{link}"  # noqa: E501
                    ),
                    link=link,
                )

                self.message_user(request, message, level=messages.WARNING)
                permission_overlap_detected.send(sender=self.__class__, message="Overlaps detected.")

        # FIXME https://github.com/saxix/django-admin-extra-buttons/issues/6, disable when changing form
        @button()  # type: ignore
        def check_overlaps(
            self, request: HttpRequest, user_temp_permission_id: int
        ) -> None:  # returned by the django-admin-extra buttons
            """Allow user to check for overlaps on demands."""
            self._check_overlaps(request, user_temp_permission_id)

        def save_related(self, request: HttpRequest, form: Any, formsets: Any, change: Any) -> None:  # noqa: ANN401
            """Override, to check for overlaps on every save."""
            super().save_related(request, form, formsets, change)
            self._check_overlaps(request, form.instance.id)

    class TemporaryPermissionCustomUserAdmin(ExtraButtonsMixin, UserAdmin):
        """Custom admin for the default User model."""

        @button()  # type: ignore
        def configure_temporary_permission(self, request: HttpRequest, obj: AbstractBaseUser) -> HttpResponse:
            """Redirect to TemporaryPermission create view with user pre-filled."""
            url = reverse("admin:django_temp_permissions_temporarypermission_add")
            return redirect(f"{url}?user={obj}")

    admin.site.unregister(get_user_model())
    admin.site.register(get_user_model(), TemporaryPermissionCustomUserAdmin)
except ImportError:
    pass  # skipping if not installed
