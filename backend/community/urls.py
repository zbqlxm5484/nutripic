from django.urls import path

from .views import (
    CommentDetailView,
    CommentListCreateView,
    PostDetailView,
    PostLikeView,
    PostListCreateView,
)

urlpatterns = [
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:post_id>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/<int:post_id>/like/', PostLikeView.as_view(), name='post-like'),
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:comment_id>/', CommentDetailView.as_view(), name='comment-detail'),
]