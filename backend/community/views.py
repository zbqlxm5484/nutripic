from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.pagination import CursorPagination, PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Comment, Post, PostLike
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    CommentUpdateSerializer,
    PostCreateUpdateSerializer,
    PostDetailSerializer,
    PostListSerializer,
)


class CommunityPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class PostCursorPagination(CursorPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    ordering = ('-created_at', '-id')


class PostListCreateView(generics.ListCreateAPIView):
    pagination_class = CommunityPagination
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        queryset = Post.objects.select_related('author').annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True),
        )

        ordering = self.request.query_params.get('ordering', 'latest')

        if ordering == 'latest':
            return queryset.order_by('-created_at', '-id')

        if ordering == 'likes':
            return queryset.order_by('-like_count', '-created_at', '-id')

        return queryset.none()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PostListSerializer
        return PostCreateUpdateSerializer

    def list(self, request, *args, **kwargs):
        ordering = request.query_params.get('ordering', 'latest')
        if ordering not in ['latest', 'likes']:
            return Response(
                {
                    'error_code': 'validation_error',
                    'message': 'Invalid ordering.',
                    'details': {
                        'ordering': ['ordering must be latest or likes.']
                    },
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if ordering == 'latest':
            queryset = self.filter_queryset(self.get_queryset())
            paginator = PostCursorPagination()
            page = paginator.paginate_queryset(queryset, request, view=self)
            serializer = self.get_serializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = PostCreateUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=request.user)
        post = self.get_queryset().get(id=post.id)
        response_serializer = PostDetailSerializer(
            post,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    lookup_url_kwarg = 'post_id'
    http_method_names = ['get', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsAuthorOrReadOnly()]

    def get_queryset(self):
        return Post.objects.select_related('author').annotate(
            like_count=Count('likes', distinct=True),
            comment_count=Count('comments', distinct=True),
        )

    def get_serializer_class(self):
        if self.request.method == 'PATCH':
            return PostCreateUpdateSerializer
        return PostDetailSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        post = self.get_object()
        serializer = PostCreateUpdateSerializer(
            post,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        post = self.get_queryset().get(id=post.id)
        response_serializer = PostDetailSerializer(
            post,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data)


class PostLikeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        PostLike.objects.get_or_create(post=post, user=request.user)

        return Response(
            {
                'post_id': post.id,
                'is_liked': True,
                'like_count': post.likes.count(),
            },
            status=status.HTTP_200_OK,
        )

    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id)
        PostLike.objects.filter(post=post, user=request.user).delete()

        return Response(
            {
                'post_id': post.id,
                'is_liked': False,
                'like_count': post.likes.count(),
            },
            status=status.HTTP_200_OK,
        )


class CommentListCreateView(generics.ListCreateAPIView):
    http_method_names = ['get', 'post', 'head', 'options']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_post(self):
        return get_object_or_404(Post, id=self.kwargs['post_id'])

    def get_queryset(self):
        post = self.get_post()
        return (
            Comment.objects
            .filter(post=post, parent__isnull=True)
            .select_related('author', 'parent')
            .prefetch_related('replies__author')
        )

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post'] = self.get_post()
        return context

    def create(self, request, *args, **kwargs):
        post = self.get_post()
        serializer = CommentCreateSerializer(
            data=request.data,
            context={
                **self.get_serializer_context(),
                'post': post,
            },
        )
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        response_serializer = CommentSerializer(
            comment,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.select_related('author', 'post', 'parent')
    lookup_url_kwarg = 'comment_id'
    permission_classes = [permissions.IsAuthenticated, IsAuthorOrReadOnly]
    http_method_names = ['patch', 'delete', 'head', 'options']

    def get_serializer_class(self):
        return CommentUpdateSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        comment = self.get_object()
        serializer = CommentUpdateSerializer(
            comment,
            data=request.data,
            partial=partial,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = CommentSerializer(
            comment,
            context=self.get_serializer_context(),
        )
        return Response(response_serializer.data)
