from django.urls import path

from .views import (
    AdminCommentDeleteView,
    AdminCommentListView,
    AdminPostDeleteView,
    AdminPostListView,
    AdminReportStatisticsView,
    AdminUserDetailView,
    AdminUserListView,
)

urlpatterns = [
    path('users/', AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:user_id>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('posts/', AdminPostListView.as_view(), name='admin-post-list'),
    path('posts/<int:post_id>/', AdminPostDeleteView.as_view(), name='admin-post-delete'),
    path('comments/', AdminCommentListView.as_view(), name='admin-comment-list'),
    path('comments/<int:comment_id>/', AdminCommentDeleteView.as_view(), name='admin-comment-delete'),
    path('reports/statistics/', AdminReportStatisticsView.as_view(), name='admin-report-statistics'),
]