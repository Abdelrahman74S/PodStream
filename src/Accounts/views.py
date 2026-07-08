from django.shortcuts import render
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import UserSerializer , UserCreateSerializer , ChangePasswordSerializer
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny , IsAuthenticated , IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView, GenericAPIView ,ListAPIView , RetrieveUpdateDestroyAPIView



User = get_user_model()


class RegisterViews(CreateAPIView):
    permission_classes = [AllowAny]
    
    serializer_class = UserCreateSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        } 
        
        response_data = {
            'user': {'username': user.username, 'email': user.email},
            'tokens': tokens,
        }
        return Response(response_data, status=status.HTTP_201_CREATED)
    
class LoginViews(TokenObtainPairView):
    serializer_class = TokenObtainPairSerializer

    
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ListUserProfileView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return User.objects.all()
        else:
            return User.objects.filter(pk=user.pk)

class UserProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg  = 'id'
    
    def get_object(self):
        user_id = self.kwargs.get('id')
        if not user_id:
            return self.request.user
        if self.request.user.is_staff:
            return get_object_or_404(User, pk=user_id)
        if str(self.request.user.pk) == str(user_id):
            return self.request.user
        raise PermissionDenied("You do not have permission to access this profile.")

class ChangePasswordView(GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        old_password = serializer.validated_data["old_password"]
        
        if not user.check_password(old_password):
            return Response(
                {"old_password": ["Wrong password."]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(serializer.validated_data["new_password"])
        
        user.save(update_fields=["password"])

        return Response({"success": "Password updated successfully"}, status=status.HTTP_200_OK)