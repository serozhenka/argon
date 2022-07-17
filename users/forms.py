from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Account

alphabet = "abcdefghijklmnopqrstuvwxyz"


class RegisterForm(UserCreationForm, forms.ModelForm):

    class Meta:
        model = Account
        fields = ('email', 'username', 'password1', 'password2')
        labels = {'password2': 'Confirm password'}

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control py-2 text-muted', 'placeholder': " "})

    def clean_username(self):
        username = self.cleaned_data['username']
        if username == username.lower():
            if username.isdecimal():
                raise forms.ValidationError('Username can not contain only numbers')
            if not all([x.isnumeric() or x == '_' or x in alphabet for x in username]):
                raise forms.ValidationError('Username can only contain lowercase letters, numbers and underscores')
        return username


class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput())
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control py-2 text-muted', 'placeholder': " "})

    def clean(self):
        if self.is_valid():
            email = self.cleaned_data.get('email')
            password = self.cleaned_data.get('password')

            if not authenticate(email=email, password=password):
                raise forms.ValidationError('Invalid credentials')


class AccountEditForm(forms.ModelForm):

    class Meta:
        model = Account
        fields = ('username', 'name', 'bio')

    def clean_username(self):
        username = self.cleaned_data['username']
        if username == username.lower():
            if username.isdecimal():
                raise forms.ValidationError('Username can not contain only numbers')
            if not all([x.isnumeric() or x == '_' or x in alphabet for x in username]):
                raise forms.ValidationError('Username can only contain lowercase letters, numbers and underscores')
        return username