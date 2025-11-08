"""Django temporary permission custom backend."""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from django_temp_permissions.models import TemporaryPermission

User = get_user_model()


class TemporaryPermissionBackend(BaseBackend):
    """Custom permission backend for temporary permissions support."""

    def get_user_permissions(self, user_obj: User, obj: str | None = None) -> set:
        """Append the temporary permissions to the list of permissions."""
        if not user_obj.is_active or user_obj.is_anonymous or obj is not None:
            return set()

        permissions = TemporaryPermission.objects.get_active_permissions(user_obj)
        perms = permissions.values_list("content_type__app_label", "codename").order_by()

        return {"%s.%s" % (ct, name) for ct, name in perms}
