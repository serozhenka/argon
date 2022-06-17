from django.contrib.auth import views as auth_views
from django.test import TestCase
from django.urls import resolve, reverse

from users import views
from users.models import Account

class TestUserUrls(TestCase):

    def setUp(self) -> None:
        self.user = Account.objects.create_user(email="test", username="test", password='test')

    def test_login_url_resolved(self):
        url = reverse('account:login')
        self.assertEqual(resolve(url).func, views.login_page)

    def test_register_url_resolved(self):
        url = reverse('account:register')
        self.assertEqual(resolve(url).func, views.register_page)

    def test_logout_url_resolved(self):
        url = reverse('account:logout')
        self.assertEqual(resolve(url).func, views.logout_page)

    def test_account_url_resolved(self):
        url = reverse('account:account', kwargs={'username': self.user.username})
        self.assertEqual(resolve(url).func, views.account_page)

    def test_account_edit_url_resolved(self):
        url = reverse('account:account-edit', kwargs={'username': self.user.username})
        self.assertEqual(resolve(url).func, views.account_edit_page)

    def test_privacy_and_security_url_resolved(self):
        url = reverse('account:privacy-security', kwargs={'username': self.user.username})
        self.assertEqual(resolve(url).func, views.privacy_and_security_page)

    def test_privacy_and_security_status_change_url_resolved(self):
        url = reverse('account:privacy-security-status-change', kwargs={'username': self.user.username})
        self.assertEqual(resolve(url).func, views.change_user_privacy_status)

    def test_crop_image_url_resolved(self):
        url = reverse('account:crop-image', kwargs={'username': self.user.username})
        self.assertEqual(resolve(url).func, views.crop_image)

    def test_password_change_url_resolved(self):
        url = reverse('account:password_change')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordChangeView)

    def test_password_change_done_url_resolved(self):
        url = reverse('account:password_change_done')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordChangeDoneView)

    def test_password_reset_url_resolved(self):
        url = reverse('account:password_reset')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetView)

    def test_password_reset_done_url_resolved(self):
        url = reverse('account:password_reset_done')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetDoneView)

    def test_password_reset_complete_url_resolved(self):
        url = reverse('account:password_reset_complete')
        self.assertEqual(resolve(url).func.view_class, auth_views.PasswordResetCompleteView)
