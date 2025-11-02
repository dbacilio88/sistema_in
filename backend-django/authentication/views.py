"""
Views for authentication app
"""
import logging

from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse

from .models import User, LoginHistory
from .permissions import IsAdmin, IsSupervisorOrAbove
from .serializers import (
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    LoginHistorySerializer,
    LoginResponseSerializer,
    LoginSerializer,
    LogoutSerializer,
    UserCreateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)
from .utils import get_client_ip, get_user_agent

logger = logging.getLogger(__name__)


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='User Login',
        description='Authenticate user and return JWT tokens',
        request=LoginSerializer,
        responses={
            200: LoginResponseSerializer,
            401: OpenApiResponse(description='Invalid credentials'),
            423: OpenApiResponse(description='Account locked'),
        }
    )
)
class LoginView(TokenObtainPairView):
    """
    User login endpoint with JWT token generation
    """
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        """
        Handle user login
        """
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            
            # Get user from validated data
            user_data = serializer.validated_data.get('user')
            user = User.objects.get(id=user_data['id'])
            
            # Create login history record
            LoginHistory.objects.create(
                user=user,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                success=True
            )
            
            logger.info(f"User {user.email} logged in successfully from {get_client_ip(request)}")
            
            return Response({
                'success': True,
                'data': serializer.validated_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log failed login attempt
            email = request.data.get('email')
            if email:
                try:
                    user = User.objects.get(email=email)
                    LoginHistory.objects.create(
                        user=user,
                        ip_address=get_client_ip(request),
                        user_agent=get_user_agent(request),
                        success=False,
                        failure_reason=str(e)
                    )
                except User.DoesNotExist:
                    pass
            
            logger.warning(f"Failed login attempt for {email} from {get_client_ip(request)}")
            
            return Response({
                'success': False,
                'error': {
                    'code': 'authentication_failed',
                    'message': 'Invalid credentials',
                    'details': serializer.errors if hasattr(serializer, 'errors') else {}
                }
            }, status=status.HTTP_401_UNAUTHORIZED)


@extend_schema(
    tags=['Authentication'],
    summary='Refresh Access Token',
    description='Get a new access token using refresh token'
)
class RefreshTokenView(TokenRefreshView):
    """
    Refresh JWT access token
    """
    permission_classes = [AllowAny]


@extend_schema_view(
    post=extend_schema(
        tags=['Authentication'],
        summary='User Logout',
        description='Logout user and blacklist refresh token',
        request=LogoutSerializer,
        responses={
            200: OpenApiResponse(description='Successfully logged out'),
            400: OpenApiResponse(description='Invalid token'),
        }
    )
)
class LogoutView(APIView):
    """
    User logout endpoint
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Handle user logout
        """
        serializer = LogoutSerializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            # Update login history
            try:
                login_record = LoginHistory.objects.filter(
                    user=request.user,
                    logout_at__isnull=True
                ).order_by('-login_at').first()
                
                if login_record:
                    login_record.logout_at = timezone.now()
                    login_record.save()
            except Exception as e:
                logger.error(f"Error updating login history: {str(e)}")
            
            logger.info(f"User {request.user.email} logged out successfully")
            
            return Response({
                'success': True,
                'message': 'Successfully logged out'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error for user {request.user.email}: {str(e)}")
            return Response({
                'success': False,
                'error': {
                    'code': 'logout_failed',
                    'message': 'Failed to logout',
                    'details': serializer.errors if hasattr(serializer, 'errors') else {}
                }
            }, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        tags=['Users'],
        summary='List Users',
        description='Get paginated list of all users (Admin/Supervisor only)'
    ),
    retrieve=extend_schema(
        tags=['Users'],
        summary='Get User Details',
        description='Get details of a specific user'
    ),
    create=extend_schema(
        tags=['Users'],
        summary='Create User',
        description='Create a new user (Admin only)',
        request=UserCreateSerializer,
        responses={201: UserSerializer}
    ),
    update=extend_schema(
        tags=['Users'],
        summary='Update User',
        description='Update user information (Admin only)',
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    ),
    partial_update=extend_schema(
        tags=['Users'],
        summary='Partial Update User',
        description='Partially update user information (Admin only)',
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    ),
    destroy=extend_schema(
        tags=['Users'],
        summary='Delete User',
        description='Deactivate user (Admin only)'
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['role', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'dni']
    ordering_fields = ['date_joined', 'last_login', 'username', 'email']
    ordering = ['-date_joined']
    
    def get_permissions(self):
        """
        Set permissions based on action
        """
        if self.action in ['create', 'destroy']:
            return [IsAuthenticated(), IsAdmin()]
        elif self.action in ['list', 'update', 'partial_update']:
            return [IsAuthenticated(), IsSupervisorOrAbove()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer
    
    def perform_destroy(self, instance):
        """
        Soft delete user by deactivating instead of deleting
        """
        instance.is_active = False
        instance.save()
        logger.info(f"User {instance.email} deactivated by {self.request.user.email}")
    
    @extend_schema(
        tags=['Users'],
        summary='Get Current User',
        description='Get authenticated user\'s information',
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Get current user information
        """
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    @extend_schema(
        tags=['Users'],
        summary='Update Current User',
        description='Update authenticated user\'s information',
        request=UserUpdateSerializer,
        responses={200: UserSerializer}
    )
    @action(detail=False, methods=['patch'])
    def update_me(self, request):
        """
        Update current user information
        """
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'data': UserSerializer(request.user).data
        })
    
    @extend_schema(
        tags=['Users'],
        summary='Change Password',
        description='Change authenticated user\'s password',
        request=ChangePasswordSerializer,
        responses={200: OpenApiResponse(description='Password changed successfully')}
    )
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """
        Change user password
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Set new password
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.password_changed_at = timezone.now()
        request.user.must_change_password = False
        request.user.save()
        
        logger.info(f"Password changed for user {request.user.email}")
        
        return Response({
            'success': True,
            'message': 'Password changed successfully'
        })
    
    @extend_schema(
        tags=['Users'],
        summary='Get Login History',
        description='Get authenticated user\'s login history',
        responses={200: LoginHistorySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def login_history(self, request):
        """
        Get user's login history
        """
        history = LoginHistory.objects.filter(user=request.user).order_by('-login_at')[:20]
        serializer = LoginHistorySerializer(history, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
