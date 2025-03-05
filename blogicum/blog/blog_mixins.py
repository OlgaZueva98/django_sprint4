from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse

from blog.models import Comment


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        return redirect('blog:post_detail', post_id=self.kwargs['post_id'])


class EditDeleteCommentMixin(LoginRequiredMixin, OnlyAuthorMixin):
    model = Comment
    template_name = 'blog/comment.html'
    slug_url_kwarg = 'comment_id'
    slug_field = 'id'

    def get_object(self):
        return get_object_or_404(
            Comment,
            pk=self.kwargs['comment_id'],
            post__pk=self.kwargs['post_id']
        )

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post_id}
        )
