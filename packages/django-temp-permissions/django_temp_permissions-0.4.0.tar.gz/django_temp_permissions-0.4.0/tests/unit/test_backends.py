import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from test_utils.factories import TemporaryPermissionFactory

User = get_user_model()


@pytest.mark.django_db
def test_backend_temp_user_permission(staff_user, change_user_perm, client):
    client.force_login(staff_user)

    user_view_url = reverse("admin:auth_user_change", kwargs={"object_id": staff_user.id})
    response = client.get(user_view_url)

    assert response.status_code == 403, "User not authorised, request is denied."

    # Add temporary permission
    TemporaryPermissionFactory(
        user_id=staff_user.id,
        permissions=[change_user_perm],
    )

    # Verify temporary permission backend provides the permission
    response = client.get(user_view_url)
    assert response.status_code == 200, "Temporary Permission Backend provides permission, allow."
    assert staff_user.username in response.content.decode('utf-8')


@pytest.mark.django_db
def test_backend_inactive_user_no_permissions(inactive_user, change_user_perm):
    TemporaryPermissionFactory(
        user_id=inactive_user.id,
        permissions=[change_user_perm],
    )

    assert inactive_user.has_perm(change_user_perm._full_name) is False

    inactive_user.is_active = True
    inactive_user.save()
    assert inactive_user.has_perm(change_user_perm._full_name) is True
