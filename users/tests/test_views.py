from django.contrib.auth import get_user
from django.test import TestCase, Client
from django.urls import reverse
from model_bakery import baker

from users.models import Account

class TestUserPublicViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.pwd = '21b4f6bcb67f57ce9487cfbd0eb91265'
        self.user = Account.objects.create_user(
            email='test@gmail.com',
            username='test',
            password=self.pwd,
        )

        self.login_url = reverse('account:login')
        self.register_url = reverse('account:register')
        self.account_page_url = reverse('account:account', kwargs={'username': self.user.username})
        self.account_edit_page_url = reverse('account:account-edit', kwargs={'username': self.user.username})
        self.privacy_and_security = reverse('account:privacy-security', kwargs={'username': self.user.username})
        self.privacy_and_security_status_change = reverse(
            'account:privacy-security-status-change', kwargs={'username': self.user.username}
        )
        self.crop_image_url = reverse('account:crop-image', kwargs={'username': self.user.username})

    def test_login_get_request(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_register_post_request(self):
        response = self.client.post(self.register_url, {
            'email': 'testing@gmail.com',
            'username': 'testing',
            'password1': self.pwd,
            'password2': self.pwd
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Account.objects.count(), 2)

    def test_register_get_request(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)

    def test_account_page_get_request(self):
        response = self.client.get(self.account_page_url)
        self.assertEqual(response.status_code, 302)

    def test_account_edit_page_get_request(self):
        response = self.client.get(self.account_edit_page_url)
        self.assertEqual(response.status_code, 302)

    def test_privacy_and_security_page_get_request(self):
        response = self.client.get(self.privacy_and_security)
        self.assertEqual(response.status_code, 302)

    def test_privacy_and_security_status_change_page_get_request(self):
        response = self.client.get(self.privacy_and_security_status_change)
        self.assertEqual(response.status_code, 302)

    def test_crop_image_get_request(self):
        response = self.client.get(self.privacy_and_security_status_change)
        self.assertEqual(response.status_code, 302)

class TestUserPrivateViews(TestCase):

    def setUp(self) -> None:
        self.client = Client()
        self.pwd = '21b4f6bcb67f57ce9487cfbd0eb91265'
        self.user = baker.make(Account)
        self.user.set_password(self.pwd)
        self.user.save()
        self.client.login(email=self.user.email, password=self.pwd)

        self.login_url = reverse('account:login')
        self.register_url = reverse('account:register')
        self.account_page_url = reverse('account:account', kwargs={'username': self.user.username})
        self.account_edit_page_url = reverse('account:account-edit', kwargs={'username': self.user.username})
        self.privacy_and_security = reverse('account:privacy-security', kwargs={'username': self.user.username})
        self.privacy_and_security_status_change = reverse(
            'account:privacy-security-status-change', kwargs={'username': self.user.username}
        )

    def test_account_page_get_request(self):
        response = self.client.get(self.account_page_url)
        self.assertEqual(response.status_code, 200)

    def test_account_edit_page_post_request(self):
        response = self.client.post(self.account_edit_page_url, {
            'username': self.user.username,
            'name': 'maria',
            'bio': 'maria playing',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_user(self.client).name, 'maria')
        self.assertEqual(get_user(self.client).bio, 'maria playing')

    def test_privacy_and_security_page_get_request(self):
        response = self.client.get(self.privacy_and_security)
        self.assertEqual(response.status_code, 200)

    def test_privacy_and_security_status_change_page_get_request(self):
        response = self.client.get(self.privacy_and_security_status_change)
        self.assertEqual(response.status_code, 302)

    def test_privacy_and_security_status_change_page_post_request(self):
        response = self.client.post(self.privacy_and_security_status_change, {
            'is_public': 'false'
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_user(self.client).is_public, False)

    def test_crop_image_get_request(self):
        response = self.client.get(self.privacy_and_security_status_change)
        self.assertEqual(response.status_code, 302)
