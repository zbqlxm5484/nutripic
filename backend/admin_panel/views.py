from collections import Counter

from django.contrib.auth import get_user_model
from django.db.models import Count
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from community.models import Comment, Post
from reports.models import Report

from .permissions import IsAdminRole
from .serializers import (
    AdminCommentSerializer,
    AdminPostSerializer,
    AdminUserSerializer,
    AdminUserUpdateSerializer,
)

User = get_user_model()


class AdminPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AdminUserListView(generics.ListAPIView):
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdminRole]
    pagination_class = AdminPagination

    def get_queryset(self):
        return User.objects.annotate(
            post_count=Count('posts', distinct=True),
            comment_count=Count('comments', distinct=True),
            report_count=Count('reports', distinct=True),
        ).order_by('-date_joined', '-id')


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdminRole]
    lookup_url_kwarg = 'user_id'
    http_method_names = ['get', 'patch', 'head', 'options']

    def get_queryset(self):
        return User.objects.annotate(
            post_count=Count('posts', distinct=True),
            comment_count=Count('comments', distinct=True),
            report_count=Count('reports', distinct=True),
        )

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return AdminUserUpdateSerializer
        return AdminUserSerializer

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = AdminUserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.is_active = serializer.validated_data['is_active']
        user.save(update_fields=['is_active'])

        user = self.get_queryset().get(id=user.id)
        response_serializer = AdminUserSerializer(user)
        return Response(response_serializer.data)


class AdminPostListView(generics.ListAPIView):
    serializer_class = AdminPostSerializer
    permission_classes = [IsAdminRole]
    pagination_class = AdminPagination

    def get_queryset(self):
        return (
            Post.objects
            .select_related('author')
            .annotate(
                like_count=Count('likes', distinct=True),
                comment_count=Count('comments', distinct=True),
            )
            .order_by('-created_at', '-id')
        )


class AdminPostDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminRole]
    lookup_url_kwarg = 'post_id'

    def get_queryset(self):
        return Post.objects.all()


class AdminCommentListView(generics.ListAPIView):
    serializer_class = AdminCommentSerializer
    permission_classes = [IsAdminRole]
    pagination_class = AdminPagination

    def get_queryset(self):
        return (
            Comment.objects
            .select_related('post', 'author', 'parent')
            .order_by('-created_at', '-id')
        )


class AdminCommentDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminRole]
    lookup_url_kwarg = 'comment_id'

    def get_queryset(self):
        return Comment.objects.all()


class AdminReportStatisticsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        reports = Report.objects.all()

        return Response({
            'report_count': reports.count(),
            'popular_health_goals': self.get_popular_health_goals(reports),
            'popular_ingredients': self.get_popular_ingredients(reports),
        })

    def get_popular_health_goals(self, reports):
        counter = Counter()

        for report in reports:
            health_goals = report.input_summary.get('health_goals', [])

            for goal in health_goals:
                if isinstance(goal, dict):
                    code = goal.get('code') or goal.get('name')
                    name = goal.get('name') or code
                else:
                    code = str(goal)
                    name = str(goal)

                if code:
                    counter[(code, name)] += 1

        return [
            {
                'code': code,
                'name': name,
                'count': count,
            }
            for (code, name), count in counter.most_common(10)
        ]

    def get_popular_ingredients(self, reports):
        counter = Counter()
        names = {}

        for report in reports:
            ingredients = report.recommended_ingredients or []

            for ingredient in ingredients:
                if not isinstance(ingredient, dict):
                    continue

                normalized_name = (
                    ingredient.get('normalized_name')
                    or ingredient.get('name_en')
                    or ingredient.get('name_ko')
                )
                name_ko = ingredient.get('name_ko') or normalized_name

                if normalized_name:
                    counter[normalized_name] += 1
                    names[normalized_name] = name_ko

        return [
            {
                'normalized_name': normalized_name,
                'name_ko': names.get(normalized_name),
                'count': count,
            }
            for normalized_name, count in counter.most_common(10)
        ]