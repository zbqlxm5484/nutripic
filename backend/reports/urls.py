from django.urls import path

from .views import (
    ReportDetailView,
    ReportListCreateView,
    ReportMessageListCreateView,
)

urlpatterns = [
    path('', ReportListCreateView.as_view(), name='report-list-create'),
    path('<int:report_id>/messages/', ReportMessageListCreateView.as_view(), name='report-message-list-create'),
    path('<int:report_id>/', ReportDetailView.as_view(), name='report-detail'),
]
