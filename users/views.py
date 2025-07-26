from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import generics
from .models import User
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, UserRegisterSerializer, UserDeleteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def perform_create(self, serializer):
        user = serializer.save()
        return user

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = CustomTokenObtainPairSerializer

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user

    def perform_update(self, serializer):
        password = serializer.validated_data.pop('password', None)
        user = serializer.save()
        if password:
            user.set_password(password)
            user.save()
        return user

class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserDeleteSerializer

    def delete(self, request, *args, **kwargs):
        serializer = UserDeleteSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.is_active = False
        user.save()
        return Response(
            {"detail": "Account successfully deleted"},
            status=status.HTTP_204_NO_CONTENT
        )