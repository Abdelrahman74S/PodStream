from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import RegisterViews, LoginViews, LogoutView, ListUserProfileView, UserProfileView , ChangePasswordView

urlpatterns = [
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', RegisterViews.as_view(), name='register'),
    path('login/', LoginViews.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', ListUserProfileView.as_view(), name='list-users'),
    path('users/<str:id>/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
]
