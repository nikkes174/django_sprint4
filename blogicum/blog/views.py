from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.utils.timezone import now
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView
)

from .constants import PAGINATE_BY
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post


class IndexListView(LoginRequiredMixin, ListView):
    template_name = 'blog/index.html'
    paginate_by = PAGINATE_BY

    def get_queryset(self):
        return Post.objects.published_filter(
            annotate_comments=True,
            select_related=True
        )


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/detail.html'
    paginate_by = PAGINATE_BY
    pk_url_kwarg = 'post_id'

    def get_object(self):
        post = super().get_object()
        if post.author == self.request.user:
            return post
        filtered_post = (
            Post.objects.published_filter(
                select_related=False,
                annotate_comments=False,
                apply_filters=True
            )
            .filter(pk=post.pk)
            .first()
        )
        if not filtered_post:
            raise Http404
        return filtered_post

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            comments=self.object.comments.all(),
            form=CommentForm()
        )


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect(self.get_object())


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'text', 'category', 'image']
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def test_func(self):
        return self.request.user == self.get_object().author

    def handle_no_permission(self):
        return redirect(self.get_object())

    def get_success_url(self):
        return self.object.get_absolute_url()


class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = PAGINATE_BY

    def get_category(self):
        return get_object_or_404(
            Category,
            is_published=True,
            slug=self.kwargs['category_slug']
        )

    def get_queryset(self):
        category = self.get_category()
        return category.posts.published_filter(
            select_related=True,
            annotate_comments=True,
        )

    def get_context_data(self, **kwargs):
        return (
            super().get_context_data(
                **kwargs,
                category=self.get_category()
            )
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    template_name = 'includes/comments.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['pk'])
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.post.get_absolute_url()


class CommentBaseViev(LoginRequiredMixin, UserPassesTestMixin, View):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def test_func(self):
        return self.request.user == self.get_object().author

    def get_success_url(self):
        return reverse('blog:post_detail', args=[self.kwargs['comment_id']])


class CommentDeleteView(CommentBaseViev, DeleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.pop('form', None)
        return context


class CommentUpdateView(CommentBaseViev, UpdateView):
    fields = ['text']


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ['first_name', 'last_name', 'email', 'username']

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile_user'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        user = self.get_object()
        return super().get_context_data(
            **kwargs,
            profile=user,
            page_obj=Paginator(
                Post.objects.published_filter(
                    apply_filters=(self.request.user != user)
                ).filter(author=user),
                PAGINATE_BY
            ).get_page(self.request.GET.get("page"))
        )
