from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Account
from .validators import username_validator


class RegisterForm(UserCreationForm, forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control py-2 text-muted', 'placeholder': " "})

    class Meta:
        model = Account
        fields = ('email', 'username', 'password1', 'password2')
        labels = {'password2': 'Confirm password'}

    def clean_username(self):
        username = self.cleaned_data['username']
        valid, message = username_validator(username)
        if not valid:
            raise forms.ValidationError(message)
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
        valid, message = username_validator(username)
        if not valid:
            raise forms.ValidationError(message)
        return username