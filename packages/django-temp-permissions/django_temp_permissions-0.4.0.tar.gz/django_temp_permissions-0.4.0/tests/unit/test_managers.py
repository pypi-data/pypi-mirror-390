from datetime import timedelta

import pytest

from django_temp_permissions.models import TemporaryPermission
from test_utils.factories import PermissionFactory, UserFactory, TemporaryPermissionFactory


@pytest.mark.django_db
def test_with_perm_active_permission():
    active_temporary_perm = TemporaryPermissionFactory()
    assert TemporaryPermission.objects.with_perm(PermissionFactory()).count() == 0, (
        "Does not return an unassigned permission"
    )

    users_with_active_perms = TemporaryPermission.objects.with_perm(
        active_temporary_perm.permissions.first()  # We only have one permission, so we can just check the first
    )
    assert users_with_active_perms.count() == 1, "Only 1 active temporary permission"
    assert users_with_active_perms.first() == active_temporary_perm.user, "The manager returns the correct user"


@pytest.mark.django_db
def test_with_perm_expired_permission(expired_temporary_permission):
    assert TemporaryPermission.objects.with_perm(expired_temporary_permission.permissions.first()).count() == 0, (
        "Does not return expired permissions"
    )


@pytest.mark.django_db
def test_with_perm_expired_and_active_permissions(expired_temporary_permission):
    user = expired_temporary_permission.user
    active_temporary_perm = TemporaryPermissionFactory(user=user)
    users_with_active_perms = TemporaryPermission.objects.with_perm(active_temporary_perm.permissions.first())
    assert users_with_active_perms.count() == 1, "The user only has one active permission"
    assert users_with_active_perms.first() == user

    assert TemporaryPermission.objects.with_perm(expired_temporary_permission.permissions.first()).count() == 0, (
        "No user has this permission because it's expired"
    )


@pytest.mark.django_db
def test_with_perm_future_permission(future_temporary_permission):
    assert TemporaryPermission.objects.with_perm(future_temporary_permission.permissions.first()).count() == 0, (
        "Does not return future permissions"
    )


@pytest.mark.django_db
def test_with_perm_active_temp_perm_and_standard_permission():
    active_temp_perm = TemporaryPermissionFactory()
    mutual_user = active_temp_perm.user

    perm = PermissionFactory(user=mutual_user)

    users_with_active_perms = TemporaryPermission.objects.with_perm(active_temp_perm.permissions.first())
    assert users_with_active_perms.count() == 1, "The user only has one active permission"
    assert users_with_active_perms.first() == mutual_user

    assert TemporaryPermission.objects.with_perm(perm).count() == 0, (
        "No user has this permission because it's assigned directly, not through temporary perm"
    )


@pytest.mark.django_db
def test_get_active_permissions_active_permission():
    active_temporary_perm = TemporaryPermissionFactory()
    assert TemporaryPermission.objects.get_active_permissions(UserFactory()).count() == 0, (
        "Does not return anything for a user without any permissions"
    )

    active_perms = TemporaryPermission.objects.get_active_permissions(active_temporary_perm.user)
    assert active_perms.count() == 1, "Only 1 active temporary permission"
    assert active_perms.first() == active_temporary_perm.permissions.first()


@pytest.mark.django_db
def test_get_active_permissions_expired_permission(expired_temporary_permission):
    assert TemporaryPermission.objects.get_active_permissions(expired_temporary_permission.user).count() == 0, (
        "Does not return expired permissions"
    )


@pytest.mark.django_db
def test_get_active_permissions_expired_and_active_permissions(expired_temporary_permission):
    active_temporary_perm = TemporaryPermissionFactory()

    active_perms = TemporaryPermission.objects.get_active_permissions(active_temporary_perm.user)
    assert active_perms.count() == 1, "Only 1 active temporary permission"
    assert active_perms.first() == active_temporary_perm.permissions.first()

    assert TemporaryPermission.objects.get_active_permissions(expired_temporary_permission.user).count() == 0, (
        "Does not return expired permissions"
    )


@pytest.mark.django_db
def test_get_active_permissions_future_permission(future_temporary_permission):
    assert TemporaryPermission.objects.get_active_permissions(future_temporary_permission.user).count() == 0, (
        "Does not return future permissions"
    )


@pytest.mark.django_db
def test_get_active_permissions_active_perm_and_standard_permission():
    active_temp_perm = TemporaryPermissionFactory()
    mutual_user = active_temp_perm.user

    PermissionFactory(user=mutual_user)

    active_perms = TemporaryPermission.objects.get_active_permissions(mutual_user)
    assert active_perms.count() == 1, "The user only has one active permission"
    assert active_perms.first() == active_temp_perm.permissions.first()


@pytest.mark.django_db
def test_overlap_with_end():
    """New temporary permission, ends within the time period of an existing one."""
    active_temp_perm = TemporaryPermissionFactory()

    new_perm = TemporaryPermissionFactory(
        user=active_temp_perm.user,
        permissions=active_temp_perm.permissions.all(),
        start_datetime=active_temp_perm.start_datetime - timedelta(days=2),
        end_datetime=active_temp_perm.end_datetime - timedelta(days=1),
    )

    overlapping_temp_perms = TemporaryPermission.objects.overlapping(new_perm)
    assert overlapping_temp_perms.count() == 1
    assert overlapping_temp_perms.first() == active_temp_perm


@pytest.mark.django_db
def test_overlap_with_start():
    """New permission starts within the time period of an existing one."""
    active_temp_perm = TemporaryPermissionFactory()

    new_perm = TemporaryPermissionFactory(
        user=active_temp_perm.user,
        permissions=active_temp_perm.permissions.all(),
        start_datetime=active_temp_perm.start_datetime + timedelta(days=1),
        end_datetime=active_temp_perm.end_datetime + timedelta(days=10),
    )

    overlapping_temp_perms = TemporaryPermission.objects.overlapping(new_perm)
    assert overlapping_temp_perms.count() == 1
    assert overlapping_temp_perms.first() == active_temp_perm


@pytest.mark.django_db
def test_has_overlapping_permission_false_before():
    """New permission completely before an existing one."""
    active_temp_perm = TemporaryPermissionFactory()

    new_perm = TemporaryPermissionFactory(
        user=active_temp_perm.user,
        permissions=active_temp_perm.permissions.all(),
        start_datetime=active_temp_perm.start_datetime - timedelta(days=20),
        end_datetime=active_temp_perm.end_datetime - timedelta(days=10),
    )

    assert TemporaryPermission.objects.overlapping(new_perm).count() == 0


@pytest.mark.django_db
def test_has_overlapping_permission_false_after():
    """New permission completely after an existing one."""
    active_temp_perm = TemporaryPermissionFactory()

    new_perm = TemporaryPermissionFactory(
        user=active_temp_perm.user,
        permissions=active_temp_perm.permissions.all(),
        start_datetime=active_temp_perm.start_datetime + timedelta(days=10),
        end_datetime=active_temp_perm.end_datetime + timedelta(days=20),
    )

    assert TemporaryPermission.objects.overlapping(new_perm).count() == 0
