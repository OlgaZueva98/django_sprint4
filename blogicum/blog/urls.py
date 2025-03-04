from django.urls import include, path

from . import views

app_name = 'blog'


post_urls = [
    path(
        '<int:post_id>/',
        views.PostDetail.as_view(),
        name='post_detail'
    ),
    path('create/', views.CreatePost.as_view(), name='create_post'),
    path(
        '<int:post_id>/edit/',
        views.EditPost.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.DeletePost.as_view(),
        name='delete_post'
    ),
    path(
        '<int:post_id>/comment/',
        views.AddComment.as_view(),
        name='add_comment'
    ),
    path(
        '<int:post_id>/edit_comment/<int:comment_id>/',
        views.EditComment.as_view(),
        name='edit_comment'
    ),
    path(
        '<int:post_id>/delete_comment/<int:comment_id>/',
        views.DeleteComment.as_view(),
        name='delete_comment'
    )
]

profile_urls = [
    path(
        '<str:username>/',
        views.ProfileDetail.as_view(),
        name='profile'
    ),
    path('<str:username>/edit/', views.EditProfile.as_view(),
         name='edit_profile'),
    path(
        '<str:username>/password_change/',
        views.PasswordChange.as_view(),
        name='password_change'
    )
]

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('category/<slug:category_slug>/', views.CategoryPosts.as_view(),
         name='category_posts'),
    path('posts/', include(post_urls)),
    path('profile/', include(profile_urls))
]
