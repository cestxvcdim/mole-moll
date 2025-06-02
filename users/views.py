import stripe

from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, \
    PasswordResetCompleteView, LoginView
from django.db.models import Q
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import CreateView, UpdateView, ListView, DetailView
from django.views import View

from publications.models import Publication
from users.forms import UserRegisterForm, UserProfileForm, UserPasswordResetForm, UserPasswordSetForm, \
    UserAuthenticationForm
from users.models import User, Subscription

from users.services import create_stripe_price, create_stripe_session


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    form_class = UserAuthenticationForm


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = True
        user.save()
        return super().form_valid(form)


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


class UserListView(LoginRequiredMixin, ListView):
    model = User
    paginate_by = 10
    ordering = ['last_name', 'first_name']

    def get_queryset(self):
        qs = super().get_queryset()
        query = self.request.GET.get('q', '').strip()
        if query:
            qs = qs.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
        return qs.order_by('last_name', 'first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    context_object_name = 'user_object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.object
        request_user = self.request.user

        is_subscribed = Subscription.objects.filter(author=author, subscriber=request_user).exists()
        if is_subscribed:
            pubs = Publication.objects.filter(author=author).order_by('-created_at')
        else:
            pubs = Publication.objects.filter(author=author, is_free=True).order_by('-created_at')

        context['is_subscribed_on_author'] = is_subscribed
        context['user_publications'] = pubs
        return context


class UserUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = User
    form_class = UserProfileForm

    def get_success_url(self):
        return reverse('users:user-detail', args=[self.kwargs['pk']])

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user == self.get_object()


class BuySubscriptionView(LoginRequiredMixin, View):
    def get(self, request, author_pk):
        author = get_object_or_404(User, pk=author_pk)

        if Subscription.objects.filter(subscriber=request.user, author=author).exists():
            return redirect('users:user-detail', pk=author_pk)

        amount_rub = 100
        price = create_stripe_price(amount_rub)

        success_path = reverse('users:subscription-success', args=[author_pk])
        success_url = request.build_absolute_uri(success_path)

        cancel_path = reverse('users:user-detail', args=[author_pk])
        cancel_url = request.build_absolute_uri(cancel_path)
        payment_metadata = {
            'author_id': str(author_pk),
            'subscriber_id': str(request.user.pk),
            'amount_rub': str(amount_rub),
        }

        session = create_stripe_session(price, success_url, cancel_url, **payment_metadata)
        return redirect(session.url, code=303)


class SubscriptionSuccessView(LoginRequiredMixin, View):
    def get(self, request, author_pk):
        author = get_object_or_404(User, pk=author_pk)

        if not Subscription.objects.filter(subscriber=request.user, author=author).exists():
            amount_rub = Decimal(request.GET.get('amount_rub', '100'))
            Subscription.objects.create(
                subscriber=request.user,
                author=author,
                price=amount_rub
            )

        return redirect('users:user-detail', pk=author_pk)
