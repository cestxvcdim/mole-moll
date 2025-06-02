import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, SetPasswordForm, \
    AuthenticationForm

from users.models import User


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update({'class': 'form-check_input'})
            elif isinstance(field, forms.DateTimeField):
                field.widget = forms.DateTimeInput(
                    attrs={
                        'type': 'datetime-local',
                        'class': 'form-control'
                    },
                    format='%Y-%m-%d %H:%M:%S'
                )
                field.input_formats = ['%Y-%m-%d %H:%M:%S']
            else:
                field.widget.attrs.update({'class': 'form-control'})


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        phone = re.sub(r"[^\d+]", "", phone)
        if phone.startswith("+"):
            if not phone.startswith("+7") or len(phone) != 12 or not phone[1:].isdigit():
                raise forms.ValidationError('Неправильный формат телефона.')
        else:
            if not phone.isdigit() or len(phone) != 11 or phone[0] not in ("7", "8"):
                raise forms.ValidationError('Неправильный формат телефона.')
            phone = "+7" + phone[1:]

        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Пользователь с таким номером уже существует.')
        return phone


class UserProfileForm(StyleFormMixin, UserChangeForm):
    class Meta:
        model = User
        fields = ('phone_number', 'first_name', 'last_name', 'email', 'country', 'avatar')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password'].widget = forms.HiddenInput()

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        phone = re.sub(r"[^\d+]", "", phone)
        if phone.startswith("+"):
            if not phone.startswith("+7") or len(phone) != 12 or not phone[1:].isdigit():
                raise forms.ValidationError('Неправильный формат телефона.')
        else:
            if not phone.isdigit() or len(phone) != 11 or phone[0] not in ("7", "8"):
                raise forms.ValidationError('Неправильный формат телефона.')
            phone = "+7" + phone[1:]

        if User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('Пользователь с таким номером уже существует.')
        return phone


class UserPasswordResetForm(StyleFormMixin, PasswordResetForm):
    class Meta:
        model = User


class UserPasswordSetForm(StyleFormMixin, SetPasswordForm):
    class Meta:
        model = User


class UserAuthenticationForm(StyleFormMixin, AuthenticationForm):
    class Meta:
        model = User
