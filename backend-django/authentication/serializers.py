"""
Serializers for authentication app
"""
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, UserRole, LoginHistory


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model
    """
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    is_account_locked = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'phone', 'dni', 'profile_image',
            'is_active', 'is_staff', 'is_account_locked',
            'date_joined', 'last_login', 'updated_at'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login', 'updated_at']


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new users
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'role', 'phone', 'dni'
        ]
    
    def validate(self, attrs):
        """
        Validate that passwords match
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Password fields did not match.'
            })
        return attrs
    
    def validate_email(self, value):
        """
        Validate email uniqueness
        """
        if User.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError('This email is already registered.')
        return value.lower()
    
    def validate_username(self, value):
        """
        Validate username uniqueness
        """
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value
    
    def validate_dni(self, value):
        """
        Validate DNI format (8 digits for Peru)
        """
        if value and (not value.isdigit() or len(value) != 8):
            raise serializers.ValidationError('DNI must be 8 digits.')
        return value
    
    def create(self, validated_data):
        """
        Create a new user with encrypted password
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information
    """
    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone', 'dni', 'profile_image'
        ]
    
    def validate_dni(self, value):
        """
        Validate DNI format
        """
        if value and (not value.isdigit() or len(value) != 8):
            raise serializers.ValidationError('DNI must be 8 digits.')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for changing password
    """
    old_password = serializers.CharField(required=True, style={'input_type': 'password'})
    new_password = serializers.CharField(
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    
    def validate(self, attrs):
        """
        Validate that new passwords match
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New password fields did not match.'
            })
        return attrs
    
    def validate_old_password(self, value):
        """
        Validate that old password is correct
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer with additional user data
    Accepts both 'username' and 'email' for authentication
    """
    # Override parent fields to make them optional
    username_field = 'username'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make username and email optional
        self.fields['username'] = serializers.CharField(required=False, allow_blank=True)
        self.fields['email'] = serializers.EmailField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        """
        Validate credentials and add custom claims
        """
        # Accept either username or email
        username_or_email = attrs.get('username') or attrs.get('email') or attrs.get(self.username_field)
        password = attrs.get('password')
        
        if not username_or_email:
            raise serializers.ValidationError({
                'detail': 'Username or email is required'
            })
        
        if not password:
            raise serializers.ValidationError({
                'detail': 'Password is required'
            })
        
        # Get user by username or email
        user = None
        try:
            # Try to get by username first
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                # Try to get by email
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                raise serializers.ValidationError({
                    'detail': 'No active account found with the given credentials'
                })
        
        # Check if account is locked
        if user.is_account_locked():
            raise serializers.ValidationError({
                'detail': f'Account is locked until {user.account_locked_until}. Please try again later.'
            })
        
        # Check if account is active
        if not user.is_active:
            raise serializers.ValidationError({
                'detail': 'Account is disabled. Please contact support.'
            })
        
        # Authenticate (Django's authenticate expects email as username since USERNAME_FIELD = 'email')
        authenticated_user = authenticate(
            request=self.context.get('request'),
            username=user.email,  # Use email because USERNAME_FIELD = 'email'
            password=password
        )
        
        if authenticated_user is None:
            # Increment failed login attempts
            user.increment_failed_login()
            
            raise serializers.ValidationError({
                'detail': 'No active account found with the given credentials'
            })
        
        # Reset failed login attempts on successful login
        authenticated_user.reset_failed_login()
        
        # Update last login
        authenticated_user.last_login = timezone.now()
        authenticated_user.save(update_fields=['last_login'])
        
        # Get tokens
        refresh = self.get_token(authenticated_user)
        
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(authenticated_user).data
        }
        
        return data
    
    @classmethod
    def get_token(cls, user):
        """
        Add custom claims to token
        """
        token = super().get_token(user)
        
        # Add custom claims
        token['email'] = user.email
        token['username'] = user.username
        token['role'] = user.role
        token['full_name'] = user.get_full_name()
        
        return token


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        style={'input_type': 'password'},
        trim_whitespace=False
    )


class LoginResponseSerializer(serializers.Serializer):
    """
    Serializer for login response
    """
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()


class LogoutSerializer(serializers.Serializer):
    """
    Serializer for logout
    """
    refresh = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """
        Validate refresh token
        """
        self.token = attrs['refresh']
        return attrs
    
    def save(self, **kwargs):
        """
        Blacklist the refresh token
        """
        try:
            RefreshToken(self.token).blacklist()
        except Exception as e:
            raise serializers.ValidationError({'detail': str(e)})


class LoginHistorySerializer(serializers.ModelSerializer):
    """
    Serializer for login history
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = LoginHistory
        fields = [
            'id', 'user', 'user_email', 'login_at', 'logout_at',
            'ip_address', 'user_agent', 'success', 'failure_reason'
        ]
        read_only_fields = ['id', 'user', 'login_at']
