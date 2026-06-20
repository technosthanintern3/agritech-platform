from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.test import TestCase, Client
from django.utils import timezone
from django.urls import reverse

from accounts.forms import AdminRegistrationForm
from accounts.models import AccessCode, AdminProfile, RegistrationOTP
from accounts.views import _finalize_registration


User = get_user_model()


class AccessCodeTests(TestCase):

    def setUp(self):
        AccessCode.objects.update_or_create(
            code_type=AccessCode.ROLE_ADMIN,
            defaults={'code_hash': make_password('ADMIN-CODE-123')},
        )
        AccessCode.objects.update_or_create(
            code_type=AccessCode.ROLE_SUPER_ADMIN,
            defaults={'code_hash': make_password('SUPER-CODE-123')},
        )

    def test_access_code_resolution(self):
        self.assertEqual(AccessCode.resolve_role('ADMIN-CODE-123'), AccessCode.ROLE_ADMIN)
        self.assertEqual(AccessCode.resolve_role('SUPER-CODE-123'), AccessCode.ROLE_SUPER_ADMIN)
        self.assertIsNone(AccessCode.resolve_role('INVALID-CODE'))

    def test_invalid_admin_registration_code_is_rejected(self):
        form = AdminRegistrationForm(
            data={
                'full_name': 'Test Admin',
                'email': 'admin@example.com',
                'phone_number': '9999999999',
                'password': 'StrongPass@123',
                'confirm_password': 'StrongPass@123',
                'admin_code': 'INVALID-CODE',
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('admin_code', form.errors)

    def test_registration_view_accepts_valid_access_code(self):
        client = Client()
        response = client.post(
            reverse('admin_register'),
            data={
                'full_name': 'Valid Admin',
                'email': 'valid-admin@example.com',
                'phone_number': '9999999991',
                'password': 'StrongPass@123',
                'confirm_password': 'StrongPass@123',
                'admin_code': 'ADMIN-CODE-123',
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn('/verify-registration/', response.url)

    def test_finalize_registration_uses_access_code_role(self):
        token = RegistrationOTP.objects.create(
            role='admin',
            email='final-admin@example.com',
            phone_number='9999999992',
            payload={
                'full_name': 'Final Admin',
                'email': 'final-admin@example.com',
                'phone_number': '9999999992',
                'password': 'StrongPass@123',
                'access_code_type': AccessCode.ROLE_ADMIN,
            },
            email_otp_hash=make_password('111111'),
            phone_otp_hash=make_password('222222'),
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        role_slug, user = _finalize_registration(token)

        self.assertEqual(role_slug, 'admin')
        profile = AdminProfile.objects.get(user=user)
        self.assertEqual(profile.role, AccessCode.ROLE_ADMIN)
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_finalize_registration_uses_super_admin_access_code_role(self):
        token = RegistrationOTP.objects.create(
            role='admin',
            email='final-super-admin@example.com',
            phone_number='9999999993',
            payload={
                'full_name': 'Final Super Admin',
                'email': 'final-super-admin@example.com',
                'phone_number': '9999999993',
                'password': 'StrongPass@123',
                'access_code_type': AccessCode.ROLE_SUPER_ADMIN,
            },
            email_otp_hash=make_password('111111'),
            phone_otp_hash=make_password('222222'),
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        role_slug, user = _finalize_registration(token)

        self.assertEqual(role_slug, 'admin')
        profile = AdminProfile.objects.get(user=user)
        self.assertEqual(profile.role, AccessCode.ROLE_SUPER_ADMIN)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
