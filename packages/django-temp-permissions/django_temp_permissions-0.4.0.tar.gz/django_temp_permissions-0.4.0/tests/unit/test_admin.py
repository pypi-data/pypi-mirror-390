from unittest.mock import Mock

import pytest
from django.contrib import messages
from django.shortcuts import reverse

from django_temp_permissions.admin import TemporaryPermissionAdmin
from django_temp_permissions.models import TemporaryPermission
from test_utils.factories import TemporaryPermissionFactory, UserFactory


@pytest.mark.django_db
def test_check_overlaps_detected_button(admin_client, monkeypatch):
    monkeypatch.setattr("django_temp_permissions.signals.permission_overlap_detected.send", mock := Mock())

    # create temp perms with same user, permission and date
    temp_perm_1 = TemporaryPermissionFactory()
    temp_perm_2 = TemporaryPermissionFactory(user=temp_perm_1.user, permissions=temp_perm_1.permissions.all())

    # First, visit the change form to set the referer - required for django-admin-extra-buttons
    change_url = reverse("admin:django_temp_permissions_temporarypermission_change", args=[temp_perm_1.id])
    admin_client.get(change_url)

    # click button in the admin
    response = admin_client.get(
        reverse("admin:django_temp_permissions_temporarypermission_check_overlaps", args=[temp_perm_1.id]),
        follow=True,
        HTTP_REFERER=change_url,  # django-admin-extra buttons redirects implicitly to HTTP_REFERRER
    )

    link_to_admin = reverse("admin:django_temp_permissions_temporarypermission_change", args=[temp_perm_2.id])

    expected_message = (
        f"One or more of the permissions you saved are already covered "
        f"for the specified time period in:"
        f'<a href="{link_to_admin}" '
        f'target="_blank"> User Temporary Permission ID {temp_perm_2.id}</a>'
    )

    actual_messages = list(response.context["messages"])

    assert len(actual_messages) == 1, "only 1 message should be returned"
    assert actual_messages[0].level == messages.WARNING, "check message type"
    assert expected_message in response.content.decode('utf-8'), "message must be displayed in the page"

    # Check signal is being sent
    assert mock.call_count == 1
    assert mock.call_args.kwargs.get("sender") == TemporaryPermissionAdmin
    assert mock.call_args.kwargs.get("message") == "Overlaps detected."


@pytest.mark.django_db
def test_check_overlaps_add_view(admin_client, monkeypatch):
    """Test that overlapping permissions are detected when saving a new permission."""
    monkeypatch.setattr("django_temp_permissions.signals.permission_overlap_detected.send", mock := Mock())

    # Create an existing temporary permission
    temp_perm_1 = TemporaryPermissionFactory()

    # Prepare data for creating a duplicate permission
    data = {
        "user": temp_perm_1.user.id,
        "permissions": list(temp_perm_1.permissions.all().values_list("id", flat=True)),
        "start_datetime_0": temp_perm_1.start_datetime.strftime("%Y-%m-%d"),
        "start_datetime_1": temp_perm_1.start_datetime.strftime("%H:%M:%S"),
        "end_datetime_0": temp_perm_1.end_datetime.strftime("%Y-%m-%d"),
        "end_datetime_1": temp_perm_1.end_datetime.strftime("%H:%M:%S"),
        "notes": "",
    }

    # Submit the form to create a new overlapping permission
    response = admin_client.post(
        reverse("admin:django_temp_permissions_temporarypermission_add"),
        data=data,
        follow=True,
    )

    # Verify both permissions were created
    assert TemporaryPermission.objects.count() == 2

    # Verify the warning message is displayed
    change_url = reverse("admin:django_temp_permissions_temporarypermission_change", args=[temp_perm_1.id])
    expected_message = (
        f"One or more of the permissions you saved are already covered "
        f"for the specified time period in:"
        f'<a href="{change_url}" '
        f'target="_blank"> User Temporary Permission ID {temp_perm_1.id}</a>'
    )
    assert expected_message in response.content.decode('utf-8'), "Warning message must be displayed on the page"

    assert mock.call_count == 1
    assert mock.call_args.kwargs.get("sender") == TemporaryPermissionAdmin
    assert mock.call_args.kwargs.get("message") == "Overlaps detected."


@pytest.mark.django_db
def test_check_overlaps_change_view(admin_client, monkeypatch):
    """Test that overlapping permissions are detected when saving a new permission."""
    monkeypatch.setattr("django_temp_permissions.signals.permission_overlap_detected.send", mock := Mock())

    # Create an existing temporary permission
    temp_perm_1 = TemporaryPermissionFactory()
    temp_perm_2 = TemporaryPermissionFactory(
        user=temp_perm_1.user,
    )

    # Prepare data for creating a duplicate permission
    data = {
        "user": temp_perm_1.user.id,
        "permissions": list(temp_perm_1.permissions.all().values_list("id", flat=True)),
        "start_datetime_0": temp_perm_1.start_datetime.strftime("%Y-%m-%d"),
        "start_datetime_1": temp_perm_1.start_datetime.strftime("%H:%M:%S"),
        "end_datetime_0": temp_perm_1.end_datetime.strftime("%Y-%m-%d"),
        "end_datetime_1": temp_perm_1.end_datetime.strftime("%H:%M:%S"),
        "notes": "",
    }

    # Add the same permission as the temp_perm 1
    response = admin_client.post(
        reverse("admin:django_temp_permissions_temporarypermission_change", kwargs={"object_id": temp_perm_2.id}),
        data=data,
        follow=True,
    )

    # Verify the warning message is displayed
    change_url = reverse("admin:django_temp_permissions_temporarypermission_change", args=[temp_perm_1.id])
    expected_message = (
        f"One or more of the permissions you saved are already covered "
        f"for the specified time period in:"
        f'<a href="{change_url}" '
        f'target="_blank"> User Temporary Permission ID {temp_perm_1.id}</a>'
    )
    assert expected_message in response.content.decode('utf-8'), "Warning message must be displayed on the page"

    assert mock.call_count == 1
    assert mock.call_args.kwargs.get("sender") == TemporaryPermissionAdmin
    assert mock.call_args.kwargs.get("message") == "Overlaps detected."


@pytest.mark.django_db
def test_configure_temporary_permission_button(admin_client):
    user = UserFactory()

    response = admin_client.get(
        reverse("admin:auth_user_configure_temporary_permission", kwargs={"obj": user.id}),
    )

    assert response.status_code == 302, "should redirect to temp perm add"

    redirect_url = response.url
    assert redirect_url == f"{reverse('admin:django_temp_permissions_temporarypermission_add')}?user={user.id}"

    redirect_response = admin_client.get(redirect_url)
    assert f'<option value="2" selected>{user.username}</option>' in redirect_response.content.decode('utf-8'), (
        "user should be pre-filled"
    )
