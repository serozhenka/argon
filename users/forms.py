from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm

from .models import Account


class RegisterForm(UserCreationForm, forms.ModelForm):

    class Meta:
        model = Account
        fields = ('email', 'username', 'password1', 'password2')
        labels = {'password2': 'Confirm password'}

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

        self.fields['email'].widget.attrs['placeholder'] = 'Enter email'
        self.fields['username'].widget.attrs['placeholder'] = 'Enter username'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm password'

    def clean_username(self):
        username = self.cleaned_data['username']
        if username == username.lower():
            if all([x.isalnum() or x == '_' for x in username]):
                return username
        raise forms.ValidationError('Username can only contain lowercase letters, numbers and underscores')


class LoginForm(forms.Form):

    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Enter email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Enter password'}))

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        for _, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

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