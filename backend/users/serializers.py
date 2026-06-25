from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'age', 'gender', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')
        return User.objects.create_user(password=password, **validated_data)

class UserSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'age', 'gender', 'role', 'created_at']
        read_only_fields = ['id', 'email', 'username', 'role', 'created_at']


class LoginUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'role']
        read_only_fields = fields

class CustomTokenObtainPairSerializer(serializers.Serializer):
    login_id = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    @classmethod
    def get_token(cls, user):
        token = RefreshToken.for_user(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        authenticate_kwargs = {
            'email': attrs['login_id'],
            'password': attrs['password'],
        }
        if 'request' in self.context:
            authenticate_kwargs['request'] = self.context['request']

        self.user = authenticate(**authenticate_kwargs)
        if not api_settings.USER_AUTHENTICATION_RULE(self.user):
            raise exceptions.AuthenticationFailed(
                'No active account found with the given credentials',
                'no_active_account',
            )

        refresh = self.get_token(self.user)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': LoginUserSerializer(self.user).data,
        }


class CustomTokenRefreshSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(write_only=True)

    def validate(self, attrs):
        try:
            refresh = RefreshToken(attrs['refresh_token'])
        except TokenError as exc:
            raise exceptions.AuthenticationFailed('Invalid refresh token') from exc
        return {'access_token': str(refresh.access_token)}
