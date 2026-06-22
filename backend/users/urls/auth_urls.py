from django.urls import path
from users.views import (
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    LogoutView,
    SignupView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='auth-signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='auth-login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
]
