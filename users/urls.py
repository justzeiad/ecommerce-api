from django.urls import path
from .views import UserCreateView, UserDetailView, CustomTokenObtainPairView, UserDeleteView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='user-register'),
    path('profile/', UserDetailView.as_view(), name='user-profile'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('profile/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]