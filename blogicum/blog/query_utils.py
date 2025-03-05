from datetime import datetime

from django.db.models import Count

from blog.models import Post


def query_posts(
    manager=Post.objects,
    is_public: bool = False,
    is_commented: bool = False
):
    queryset = manager.select_related(
        'category',
        'author',
        'location'
    )
    if is_public:
        queryset = queryset.filter(
            is_published=True,
            pub_date__lt=datetime.now(),
            category__is_published=True
        )
    if is_commented:
        queryset = queryset.order_by(
            '-pub_date'
        ).annotate(comment_count=Count('comments')).all()

    return queryset
