"""
Test cases for authentication API endpoints
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User, UserRole, LoginHistory


class LoginAPITest(APITestCase):
    """Test cases for login endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.login_url = reverse('login')
        
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='SecurePass123!',
            first_name='Test',
            last_name='User',
            is_active=True
        )
    
    def test_login_success(self):
        """Test successful login"""
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertIn('user', response.data['data'])
        
        # Check login history
        self.assertTrue(LoginHistory.objects.filter(user=self.user, success=True).exists())
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        data = {
            'email': 'test@example.com',
            'password': 'WrongPassword'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
    def test_login_inactive_user(self):
        """Test login with inactive user"""
        self.user.is_active = False
        self.user.save()
        
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_locked_account(self):
        """Test login with locked account"""
        self.user.lock_account(duration_minutes=30)
        
        data = {
            'email': 'test@example.com',
            'password': 'SecurePass123!'
        }
        
        response = self.client.post(self.login_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = self.client.post(self.login_url, {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutAPITest(APITestCase):
    """Test cases for logout endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.logout_url = reverse('logout')
        
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='SecurePass123!'
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = str(self.refresh.access_token)
    
    def test_logout_success(self):
        """Test successful logout"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'refresh': str(self.refresh)
        }
        
        response = self.client.post(self.logout_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
    
    def test_logout_without_token(self):
        """Test logout without authentication"""
        response = self.client.post(self.logout_url, {})
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_invalid_refresh_token(self):
        """Test logout with invalid refresh token"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        data = {
            'refresh': 'invalid_token'
        }
        
        response = self.client.post(self.logout_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAPITest(APITestCase):
    """Test cases for user management endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='AdminPass123!',
            role=UserRole.ADMIN
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            username='user',
            password='UserPass123!',
            role=UserRole.OPERATOR
        )
        
        # Get tokens for admin
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(refresh.access_token)
    
    def test_list_users_as_admin(self):
        """Test listing users as admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        url = reverse('user-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
    
    def test_create_user_as_admin(self):
        """Test creating user as admin"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
        
        url = reverse('user-list')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'NewPass123!',
            'password_confirm': 'NewPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'role': UserRole.OPERATOR
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@example.com').exists())
    
    def test_get_current_user(self):
        """Test getting current user information"""
        refresh = RefreshToken.for_user(self.regular_user)
        token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['email'], 'user@example.com')
    
    def test_update_current_user(self):
        """Test updating current user information"""
        refresh = RefreshToken.for_user(self.regular_user)
        token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-update-me')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'Updated')
        self.assertEqual(self.regular_user.last_name, 'Name')
    
    def test_change_password(self):
        """Test changing password"""
        refresh = RefreshToken.for_user(self.regular_user)
        token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-change-password')
        data = {
            'old_password': 'UserPass123!',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertTrue(self.regular_user.check_password('NewPassword123!'))
    
    def test_change_password_wrong_old_password(self):
        """Test changing password with wrong old password"""
        refresh = RefreshToken.for_user(self.regular_user)
        token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-change-password')
        data = {
            'old_password': 'WrongPassword',
            'new_password': 'NewPassword123!',
            'new_password_confirm': 'NewPassword123!'
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_get_login_history(self):
        """Test getting login history"""
        # Create some login history
        LoginHistory.objects.create(
            user=self.regular_user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=True
        )
        
        refresh = RefreshToken.for_user(self.regular_user)
        token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-login-history')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 1)


class PermissionTest(APITestCase):
    """Test cases for permission classes"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create users with different roles
        self.admin = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='Pass123!',
            role=UserRole.ADMIN
        )
        
        self.supervisor = User.objects.create_user(
            email='supervisor@example.com',
            username='supervisor',
            password='Pass123!',
            role=UserRole.SUPERVISOR
        )
        
        self.operator = User.objects.create_user(
            email='operator@example.com',
            username='operator',
            password='Pass123!',
            role=UserRole.OPERATOR
        )
    
    def test_admin_can_create_user(self):
        """Test that admin can create users"""
        refresh = RefreshToken.for_user(self.admin)
        token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-list')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Pass123!',
            'password_confirm': 'Pass123!',
            'role': UserRole.OPERATOR
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_operator_cannot_create_user(self):
        """Test that operator cannot create users"""
        refresh = RefreshToken.for_user(self.operator)
        token = str(refresh.access_token)
        
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('user-list')
        data = {
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'Pass123!',
            'password_confirm': 'Pass123!',
            'role': UserRole.OPERATOR
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
