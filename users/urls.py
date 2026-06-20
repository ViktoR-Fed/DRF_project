from django.urls import path
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView, TokenVerifyView)

from users.apps import UsersConfig
from users.views import (PaymentViewSet, UserDetailView, UserListView,
                         UserProfileView, UserRegistrationView)

app_name = UsersConfig.name

router = SimpleRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    # Пользователи
    path("users/profile/", UserProfileView.as_view(), name="user_profile"),
    path("api/register/", UserRegistrationView.as_view(), name="user_register"),
    path("api/users/", UserListView.as_view(), name="user_list"),
    path("api/users/<int:pk>/", UserDetailView.as_view(), name="user_detail"),
    # JWT токены
    path("token/", TokenObtainPairView.as_view(), name="token"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
] + router.urls
