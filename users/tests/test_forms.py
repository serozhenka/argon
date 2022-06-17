from django.test import TestCase
from model_bakery import baker

from users.forms import RegisterForm, LoginForm, AccountEditForm
from users.models import Account

class TestUserForms(TestCase):

    def setUp(self) -> None:
        self.pwd = '21b4f6bcb67f57ce9487cfbd0eb91265'
        self.user = baker.make(Account)
        self.user2 = baker.make(Account)
        self.user.set_password(self.pwd)
        self.user.save()

    def test_login_form_valid_data(self):
        form = LoginForm(data={
            'email': self.user.email,
            'password': self.pwd,
        })
        self.assertTrue(form.is_valid())

    def test_login_form_invalid_data(self):
        form = LoginForm(data={
            'email': self.user.email + "df",
            'password': self.pwd + "df",
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) > 0)

    def test_login_form_blank_data(self):
        form = LoginForm(data={})
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) > 0)

    def test_register_form_valid_data(self):
        form = RegisterForm(data={
            'email': 'testing2@gmail.com',
            'username': 'testing2',
            'password1': self.pwd,
            'password2': self.pwd,
        })
        self.assertTrue(form.is_valid())

    def test_register_form_invalid_data(self):
        form = RegisterForm(data={
            'email': 'testing2@gmail',
            'username': 'testing2',
            'password1': '1',
            'password2': '1',
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) > 0)

    def test_register_form_blank_data(self):
        form = RegisterForm(data={})
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) > 0)

    def test_account_edit_form_valid_data(self):
        form = AccountEditForm(instance=self.user, data={
            'username': self.user.username,
            'name': 'maria',
            'bio': 'mari playing',
        })
        self.assertTrue(form.is_valid())

    def test_account_edit_form_invalid_data(self):
        form = AccountEditForm(instance=self.user, data={
            'username': self.user2.username,
            'name': 'maria',
            'bio': 'mari playing',
        })
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) > 0)

    def test_account_edit_form_blank_data(self):
        form = AccountEditForm(instance=self.user, data={})
        self.assertFalse(form.is_valid())
        self.assertTrue(len(form.errors) > 0)