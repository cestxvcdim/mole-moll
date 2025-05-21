import secrets

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, LoginView
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, TemplateView, ListView, DetailView
from django.core.mail import send_mail

from config import settings
from users.forms import UserRegisterForm, UserProfileForm, UserPasswordResetForm, UserPasswordSetForm, \
    UserAuthenticationForm, UserModeratorForm
from users.models import User


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserAuthenticationForm


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save()
        user.is_active = False

        token = secrets.token_hex(16)
        user.token = token
        user.save()

        host = self.request.get_host()
        url = f'http://{host}/users/confirm_register/{token}'

        send_mail(
            subject='Подтверждение регистрации',
            message=f'Здравствуйте, перейдите по ссылке для подтверждения почты {url}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email]
        )

        return super().form_valid(form)


class RegisterConfirmView(TemplateView):
    template_name = 'users/confirm_register.html'
    def post(self, request, *args, **kwargs):
        token = kwargs.get('token')
        user = get_object_or_404(User, token=token)
        user.is_active = True
        user.save()
        return redirect(reverse('users:login'))


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


class UserPasswordResetView(PasswordResetView):
    template_name = 'users/password_reset_form.html'
    email_template_name = 'users/password_reset_email.html'
    form_class = UserPasswordResetForm
    success_url = reverse_lazy('users:password_reset_done')


class UserPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/password_reset_done.html'


class UserPasswordResetConfirmView(PasswordResetConfirmView):
    form_class = UserPasswordSetForm
    template_name = 'users/password_reset_confirm.html'
    success_url = reverse_lazy('users:password_reset_complete')


class UserPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/password_reset_complete.html'


class UserListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = User

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name="Manager").exists()


class UserDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = User
    context_object_name = 'user_object'

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.groups.filter(name="Manager").exists()


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserModeratorForm

    def get_success_url(self):
        return reverse('users:user_detail', args=[self.kwargs['pk']])

    def test_func(self):
        user = self.request.user
        return (user.is_superuser or user.groups.filter(name="Manager").exists()) and user != self.get_object() and not self.get_object().is_superuser
