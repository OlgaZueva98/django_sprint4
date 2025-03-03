from django.shortcuts import get_object_or_404, redirect
from blog.models import Post, Category, Comment
from datetime import datetime
from django.contrib.auth import get_user_model
from django.views.generic import (CreateView, ListView, UpdateView,
                                  DeleteView, DetailView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse_lazy, reverse
from .forms import PostForm, CommentForm
from django.db.models import Count


POST_LIMIT = 10
User = get_user_model()


def query_posts():
    return Post.objects.select_related(
        'category',
        'author',
        'location'
    ).filter(
        is_published=True,
        pub_date__lt=datetime.now(),
        category__is_published=True
    ).order_by('-pub_date')


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        object = self.get_object()
        return redirect('blog:post_detail', post_id=object.pk)


class Index(ListView):
    model = Post
    ordering = '-pub_date'
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        posts = query_posts().annotate(comment_count=Count('comments')).all()
        return posts


class PostDetail(DetailView):
    model = Post
    slug_url_kwarg = 'post_id'
    slug_field = 'pk'
    context_object_name = 'post'
    template_name = 'blog/detail.html'

    def get_object(self):
        post = get_object_or_404(
            Post.objects.select_related(
                'author'
            ),
            pk=self.kwargs['post_id']
        )

        if self.request.user.username != post.author.username:
            return get_object_or_404(
                query_posts(),
                pk=self.kwargs['post_id']
            )
        else:
            return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryPosts(MultipleObjectMixin, DetailView):
    model = Category
    slug_url_kwarg = 'category_slug'
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = query_posts().filter(
            category__slug=self.object.slug
        )
        context = super().get_context_data(
            object_list=object_list,
            category=get_object_or_404(
                Category.objects.filter(is_published=True),
                slug=self.object.slug
            )
        )

        return context


class ProfileDetail(MultipleObjectMixin, DetailView):
    model = User
    slug_url_kwarg = 'username'
    slug_field = 'username'
    paginate_by = 10
    template_name = 'blog/profile.html'

    def get_context_data(self, **kwargs):
        object_list = Post.objects.select_related(
            'category',
            'author',
            'location'
        ).filter(
            author__username=self.object.username
        ).order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comments')).all()

        if self.request.user.username != self.object.username:
            object_list = object_list.filter(
                is_published=True,
                pub_date__lt=datetime.now(),
                category__is_published=True
            )

        context = super().get_context_data(
            object_list=object_list,
            profile=User.objects.get(username=self.object.username)
        )

        return context


class EditProfile(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    fields = ['first_name', 'last_name', 'username', 'email']

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class PasswordChange(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    slug_url_kwarg = 'username'
    slug_field = 'username'
    fields = ['password']

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


class CreatePost(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('blog:profile', kwargs={'username': self.request.user})


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


class AddComment(LoginRequiredMixin, CreateView):
    comment = None
    model = Comment
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)


class EditComment(LoginRequiredMixin, OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    slug_url_kwarg = 'comment_id'
    slug_field = 'id'


class DeleteComment(LoginRequiredMixin, OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    slug_url_kwarg = 'comment_id'
    slug_field = 'id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post_id}
        )
