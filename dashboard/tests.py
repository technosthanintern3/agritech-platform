from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import AccessCode, AdminProfile


User = get_user_model()


class DashboardAccessControlTests(TestCase):

    def setUp(self):
        self.client = Client()
        AccessCode.objects.update_or_create(
            code_type=AccessCode.ROLE_ADMIN,
            defaults={'code_hash': make_password('ADMIN-CODE-123')},
        )
        AccessCode.objects.update_or_create(
            code_type=AccessCode.ROLE_SUPER_ADMIN,
            defaults={'code_hash': make_password('SUPER-CODE-123')},
        )

        self.super_admin_user = User.objects.create_user(
            username='superadmin',
            email='superadmin@example.com',
            password='StrongPass@123',
            first_name='Super',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        self.super_admin_profile = AdminProfile.objects.create(
            user=self.super_admin_user,
            full_name='Super Admin',
            phone_number='9000000001',
            role=AdminProfile.ROLE_SUPER_ADMIN,
            email_verified=True,
            phone_verified=True,
        )

        self.normal_admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='StrongPass@123',
            first_name='Admin',
            is_staff=True,
            is_superuser=False,
            is_active=True,
        )
        self.normal_admin_profile = AdminProfile.objects.create(
            user=self.normal_admin_user,
            full_name='Normal Admin',
            phone_number='9000000002',
            role=AdminProfile.ROLE_ADMIN,
            email_verified=True,
            phone_verified=True,
        )

    def _admin_payload(self, profile, role):
        return {
            'first_name': profile.full_name,
            'email': profile.user.email,
            'username': profile.user.username,
            'is_active': 'on',
            'role': role,
            'phone_number': profile.phone_number,
        }

    def test_admin_login_and_dashboard_still_work(self):
        response = self.client.post(
            reverse('admin_login'),
            data={'username': 'admin', 'password': 'StrongPass@123'},
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin_dashboard'))

        dashboard_response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(dashboard_response.status_code, 200)

    def test_access_code_management_visible_only_to_super_admin(self):
        self.client.force_login(self.super_admin_user)
        super_response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(super_response.status_code, 200)
        self.assertContains(super_response, 'Access Code Management')

        self.client.force_login(self.normal_admin_user)
        admin_response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(admin_response.status_code, 200)
        self.assertNotContains(admin_response, 'Access Code Management')

    def test_access_code_management_requires_super_admin(self):
        self.client.force_login(self.normal_admin_user)
        response = self.client.get(reverse('access_code_management'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('admin_dashboard'))

        self.client.force_login(self.super_admin_user)
        super_response = self.client.get(reverse('access_code_management'))
        self.assertEqual(super_response.status_code, 200)
        self.assertContains(super_response, 'Access Code Management')

    def test_super_admin_can_promote_and_demote_admins(self):
        target_user = User.objects.create_user(
            username='targetadmin',
            email='target-admin@example.com',
            password='StrongPass@123',
            first_name='Target',
            is_staff=True,
            is_superuser=False,
            is_active=True,
        )
        target_profile = AdminProfile.objects.create(
            user=target_user,
            full_name='Target Admin',
            phone_number='9000000003',
            role=AdminProfile.ROLE_ADMIN,
            email_verified=True,
            phone_verified=True,
        )

        self.client.force_login(self.super_admin_user)
        promote_response = self.client.post(
            reverse('admin_edit', args=[target_profile.pk]),
            data=self._admin_payload(target_profile, AdminProfile.ROLE_SUPER_ADMIN),
        )
        self.assertEqual(promote_response.status_code, 302)
        target_profile.refresh_from_db()
        self.assertEqual(target_profile.role, AdminProfile.ROLE_SUPER_ADMIN)
        self.assertTrue(target_profile.user.is_superuser)

        secondary_super_user = User.objects.create_user(
            username='secondsuper',
            email='second-super@example.com',
            password='StrongPass@123',
            first_name='Second',
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )
        secondary_super_profile = AdminProfile.objects.create(
            user=secondary_super_user,
            full_name='Secondary Super Admin',
            phone_number='9000000004',
            role=AdminProfile.ROLE_SUPER_ADMIN,
            email_verified=True,
            phone_verified=True,
        )

        demote_response = self.client.post(
            reverse('admin_edit', args=[secondary_super_profile.pk]),
            data=self._admin_payload(secondary_super_profile, AdminProfile.ROLE_ADMIN),
        )
        self.assertEqual(demote_response.status_code, 302)
        secondary_super_profile.refresh_from_db()
        self.assertEqual(secondary_super_profile.role, AdminProfile.ROLE_ADMIN)
        self.assertFalse(secondary_super_profile.user.is_superuser)

    def test_normal_admin_cannot_delete_super_admin(self):
        self.client.force_login(self.normal_admin_user)
        response = self.client.post(reverse('admin_delete', args=[self.super_admin_profile.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(AdminProfile.objects.filter(pk=self.super_admin_profile.pk).exists())
