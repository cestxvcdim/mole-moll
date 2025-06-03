from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q

from publications.forms import PublicationForm, CommentaryForm
from publications.models import Publication, Commentary

from users.models import Subscription


class PublicationListView(LoginRequiredMixin, ListView):
    model = Publication
    paginate_by = 5
    ordering = ['-created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        query = self.request.GET.get('q', '').strip()

        qs = qs.filter(
            Q(is_free=True) |
            Q(author__own_sub__subscriber=user) |
            Q(author=user)
        ).distinct()

        if query:
            qs = qs.filter(
                Q(title__icontains=query) |
                Q(body__icontains=query)
            )

        return qs.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '').strip()
        return context


class PublicationDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Publication

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.views_count += 1
        self.object.save()
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)

    def test_func(self):
        publication = self.get_object()
        user = self.request.user
        if publication.is_free or publication.author == user or user.is_superuser:
            return True
        elif Subscription.objects.filter(author=publication.author, subscriber=user).exists():
            return True
        return False


class PublicationCreateView(LoginRequiredMixin, CreateView):
    model = Publication
    form_class = PublicationForm
    success_url = reverse_lazy('publications:publication-list')

    def form_valid(self, form):
        if form.is_valid():
            pub = form.save()
            user = self.request.user
            pub.author = user
            pub.save()

        return super().form_valid(form)


class PublicationUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Publication
    form_class = PublicationForm

    def get_success_url(self):
        return reverse('publications:publication-detail', args=[self.kwargs['pk']])

    def test_func(self):
        user = self.request.user
        if user == self.get_object().author or user.is_superuser:
            return True
        return False


class PublicationDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Publication
    success_url = reverse_lazy('publications:publication-list')

    def test_func(self):
        user = self.request.user
        if user == self.get_object().author or user.is_superuser:
            return True
        return False


@login_required
def add_comment(request, pk):
    publication = get_object_or_404(Publication, pk=pk)

    if request.method == 'POST':
        body = request.POST.get('body', '').strip()
        if body:
            Commentary.objects.create(
                author=request.user,
                publication=publication,
                body=body
            )
    return redirect('publications:publication-detail', pk=pk)


@login_required
def edit_comment(request, pk):
    comment = get_object_or_404(Commentary, pk=pk)

    if request.user != comment.author and not request.user.is_superuser:
        return redirect('publications:publication-detail', pk=comment.publication.pk)

    if request.method == 'POST':
        form = CommentaryForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('publications:publication-detail', pk=comment.publication.pk)
    else:
        form = CommentaryForm(instance=comment)

    return render(request, 'publications/commentary_form.html', {
        'form': form,
        'comment': comment,
        'publication': comment.publication,
    })


@login_required
def delete_comment(request, pk):
    comment = get_object_or_404(Commentary, pk=pk)
    pub_pk = comment.publication.pk

    if request.user != comment.author and not request.user.is_superuser:
        return redirect('publications:publication-detail', pk=pub_pk)

    if request.method == 'POST':
        comment.delete()
        return redirect('publications:publication-detail', pk=pub_pk)

    return render(request, 'publications/commentary_confirm_delete.html', {
        'comment': comment,
        'publication': comment.publication,
    })


@login_required
def toggle_publication_like(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    user = request.user

    if user in publication.likes.all():
        publication.likes.remove(user)
    else:
        publication.likes.add(user)

    return redirect('publications:publication-detail', pk=pk)


@login_required
def toggle_comment_like(request, pk):
    comment = get_object_or_404(Commentary, pk=pk)
    user = request.user
    pub_pk = comment.publication.pk

    if user in comment.likes.all():
        comment.likes.remove(user)
    else:
        comment.likes.add(user)

    return redirect('publications:publication-detail', pk=pub_pk)
