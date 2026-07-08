from rest_framework import serializers
from .models import User

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