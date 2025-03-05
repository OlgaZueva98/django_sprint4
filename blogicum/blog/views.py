from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .blog_mixins import OnlyAuthorMixin, EditDeleteCommentMixin
from .forms import CommentForm, PostForm
from .query_utils import query_posts

from blog.models import Category, Comment, Post


User = get_user_model()


class Index(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = settings.POST_LIMIT

    def get_queryset(self):
        return query_posts(is_public=True, is_commented=True)


class RegisterUser(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')


class PostDetail(DetailView):
    model = Post
    slug_url_kwarg = 'post_id'
    slug_field = 'pk'
    context_object_name = 'post'
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(
            query_posts(),
            pk=self.kwargs['post_id']
        )

        if self.request.user != post.author:
            return get_object_or_404(
                query_posts(is_public=True),
                pk=self.kwargs['post_id']
            )
        else:
            return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryPosts(ListView):
    model = Category
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'
    paginate_by = settings.POST_LIMIT

    def get_queryset(self):
        self.category = get_object_or_404(
            Category.objects.filter(is_published=True),
            slug=self.kwargs['category_slug']
        )
        return query_posts(
            manager=self.category.posts,
            is_public=True,
            is_commented=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['category'] = self.category

        return context


class ProfileDetail(ListView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    paginate_by = settings.POST_LIMIT
    template_name = 'blog/profile.html'

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs['username'])
        is_public = self.request.user != self.user

        return query_posts(
            manager=self.user.posts,
            is_public=is_public,
            is_commented=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['profile'] = self.user

        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PasswordChange(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    fields = ['password']

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class EditPost(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    slug_url_kwarg = 'post_id'
    slug_field = 'pk'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'post_id': self.object.pk})


class DeletePost(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    slug_url_kwarg = 'post_id'
    slug_field = 'pk'
    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['form'] = PostForm(
            instance=self.object
        )

        return context


class AddComment(LoginRequiredMixin, CreateView):
    comment = None
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        return super().form_valid(form)


class EditComment(EditDeleteCommentMixin, UpdateView):
    form_class = CommentForm


class DeleteComment(EditDeleteCommentMixin, DeleteView):
    pass
