from rest_framework import serializers
from .models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


class UserSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'role', 'profile_picture', 'bio', 'created_at', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.RegexField(
        write_only=True, 
        required=True, 
        error_messages={'invalid': 'Password must be at least 8 chars with uppercase, number & symbol'},
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    )
    confirm_password = serializers.RegexField(
        write_only=True, 
        required=True, 
        error_messages={'invalid': 'Password must be at least 8 chars with uppercase, number & symbol'},
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    )
    profile_picture = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password' , 'confirm_password', 'role', 'profile_picture', 'bio']
        extra_kwargs = {
            'password': {'write_only': True},
        }
        
    
    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        user = User.objects.create_user(**validated_data)
        return user
    
    
class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True, required=True)
    
    new_password = serializers.RegexField(
        write_only=True, 
        required=True, 
        error_messages={'invalid': 'Password must be at least 8 chars with uppercase, number & symbol'},
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    )
    
    confirm_new_password = serializers.RegexField(
        write_only=True, 
        required=True, 
        error_messages={'invalid': 'Password must be at least 8 chars with uppercase, number & symbol'},
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    ) 
    
    class Meta:
        model = User
        fields = ['old_password', 'new_password', 'confirm_new_password']
    
    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data



class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("No user is registered with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    uidb64 = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.RegexField(
        write_only=True, 
        required=True, 
        error_messages={'invalid': 'Password must be at least 8 chars with uppercase, number & symbol'},
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    )
    confirm_new_password = serializers.RegexField(
        write_only=True, 
        required=True, 
        error_messages={'invalid': 'Password must be at least 8 chars with uppercase, number & symbol'},
        regex=r'^(?=.*[A-Z])(?=.*\d)(?=.*[\W_]).{8,}$'
    )

    def validate(self, data):
        if data['new_password'] != data['confirm_new_password']:
            raise serializers.ValidationError({"confirm_new_password": "Passwords do not match."})
        
        try:
            uid = force_str(urlsafe_base64_decode(data['uidb64']))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({"uidb64": "Invalid or expired user ID."})
            
        if not default_token_generator.check_token(user, data['token']):
            raise serializers.ValidationError({"token": "Invalid or expired token."})
            
        self.user = user
        return data

    def save(self):
        user = self.user
        user.set_password(self.validated_data['new_password'])
        user.save(update_fields=['password'])
        return user