from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm, \
    AuthenticationForm

from publications.forms import StyleFormMixin
from users.models import User


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ('phone_number', 'password1', 'password2')


class UserProfileForm(StyleFormMixin, UserChangeForm):
    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name', 'email', 'country', 'avatar')


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()


class UserPasswordResetForm(StyleFormMixin, PasswordResetForm):
    class Meta:
        model = User


class UserPasswordSetForm(StyleFormMixin, SetPasswordForm):
    class Meta:
        model = User


class UserAuthenticationForm(StyleFormMixin, AuthenticationForm):
    class Meta:
        model = User


class UserModeratorForm(StyleFormMixin, UserChangeForm):
    class Meta:
        model = User
        fields = ('is_active', )


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()
