from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    SignupSerializer,
    UserSerializer,
)

User = get_user_model()


def error_response(error_code, message, status_code, details=None):
    return Response(
        {
            'error_code': error_code,
            'message': message,
            'details': details or {},
        },
        status=status_code,
    )


class SignupView(generics.CreateAPIView):
    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return error_response(
                'validation_error',
                'refresh_token is required.',
                status.HTTP_400_BAD_REQUEST,
                {'refresh_token': ['This field is required.']},
            )

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception:
            return error_response(
                'validation_error',
                'Invalid refresh_token.',
                status.HTTP_400_BAD_REQUEST,
                {'refresh_token': ['Invalid token.']},
            )

        return Response(status=status.HTTP_204_NO_CONTENT)


class MeView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def delete(self, request, *args, **kwargs):
        request.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        user = request.user
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            details = {}
            if not current_password:
                details['current_password'] = ['This field is required.']
            if not new_password:
                details['new_password'] = ['This field is required.']
            return error_response(
                'validation_error',
                'current_password and new_password are required.',
                status.HTTP_400_BAD_REQUEST,
                details,
            )

        if not user.check_password(current_password):
            return error_response(
                'validation_error',
                'Current password does not match.',
                status.HTTP_400_BAD_REQUEST,
                {'current_password': ['Current password does not match.']},
            )

        try:
            validate_password(new_password, user=user)
        except ValidationError as exc:
            return error_response(
                'validation_error',
                'New password is invalid.',
                status.HTTP_400_BAD_REQUEST,
                {'new_password': list(exc.messages)},
            )

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyPageView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'age': user.age,
                'gender': user.gender,
            },
            'report_count': user.reports.count(),
            'post_count': user.posts.count(),
            'comment_count': user.comments.count(),
        })
