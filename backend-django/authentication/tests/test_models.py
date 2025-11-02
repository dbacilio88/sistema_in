"""
Test cases for authentication models
"""
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta

from authentication.models import User, UserRole, LoginHistory


class UserModelTest(TestCase):
    """Test cases for User model"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'SecurePass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'role': UserRole.OPERATOR
        }
    
    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('SecurePass123!'))
        self.assertEqual(user.role, UserRole.OPERATOR)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)
    
    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            username='admin',
            password='AdminPass123!'
        )
        
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_active)
        self.assertEqual(user.role, UserRole.ADMIN)
    
    def test_user_str(self):
        """Test user string representation"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'test@example.com (Operator)')
    
    def test_get_full_name(self):
        """Test get_full_name method"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_full_name(), 'Test User')
        
        # Test with no first/last name
        user_no_name = User.objects.create_user(
            email='noname@example.com',
            username='noname',
            password='Pass123!'
        )
        self.assertEqual(user_no_name.get_full_name(), 'noname')
    
    def test_get_short_name(self):
        """Test get_short_name method"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(user.get_short_name(), 'Test')
    
    def test_is_account_locked(self):
        """Test account locking functionality"""
        user = User.objects.create_user(**self.user_data)
        
        # Account should not be locked initially
        self.assertFalse(user.is_account_locked())
        
        # Lock account
        user.lock_account(duration_minutes=30)
        self.assertTrue(user.is_account_locked())
        
        # Test expired lock
        user.account_locked_until = timezone.now() - timedelta(minutes=1)
        user.save()
        self.assertFalse(user.is_account_locked())
    
    def test_increment_failed_login(self):
        """Test failed login attempt tracking"""
        user = User.objects.create_user(**self.user_data)
        
        # Increment failed attempts
        for i in range(4):
            user.increment_failed_login(max_attempts=5)
            self.assertEqual(user.failed_login_attempts, i + 1)
            self.assertFalse(user.is_account_locked())
        
        # 5th attempt should lock account
        user.increment_failed_login(max_attempts=5)
        self.assertEqual(user.failed_login_attempts, 5)
        self.assertTrue(user.is_account_locked())
    
    def test_reset_failed_login(self):
        """Test resetting failed login attempts"""
        user = User.objects.create_user(**self.user_data)
        
        # Set failed attempts
        user.failed_login_attempts = 3
        user.save()
        
        # Reset
        user.reset_failed_login()
        self.assertEqual(user.failed_login_attempts, 0)
    
    def test_role_checks(self):
        """Test role checking methods"""
        admin_user = User.objects.create_user(
            email='admin@example.com',
            username='admin',
            password='Pass123!',
            role=UserRole.ADMIN
        )
        
        supervisor_user = User.objects.create_user(
            email='supervisor@example.com',
            username='supervisor',
            password='Pass123!',
            role=UserRole.SUPERVISOR
        )
        
        operator_user = User.objects.create_user(
            email='operator@example.com',
            username='operator',
            password='Pass123!',
            role=UserRole.OPERATOR
        )
        
        # Test is_admin
        self.assertTrue(admin_user.is_admin())
        self.assertFalse(supervisor_user.is_admin())
        self.assertFalse(operator_user.is_admin())
        
        # Test is_supervisor
        self.assertTrue(admin_user.is_supervisor())
        self.assertTrue(supervisor_user.is_supervisor())
        self.assertFalse(operator_user.is_supervisor())
        
        # Test is_operator
        self.assertTrue(admin_user.is_operator())
        self.assertTrue(supervisor_user.is_operator())
        self.assertTrue(operator_user.is_operator())
    
    def test_has_role(self):
        """Test has_role method"""
        user = User.objects.create_user(**self.user_data)
        
        self.assertTrue(user.has_role(UserRole.OPERATOR))
        self.assertFalse(user.has_role(UserRole.ADMIN))
        self.assertTrue(user.has_role(UserRole.OPERATOR, UserRole.SUPERVISOR))


class LoginHistoryModelTest(TestCase):
    """Test cases for LoginHistory model"""
    
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Pass123!'
        )
    
    def test_create_login_history(self):
        """Test creating login history record"""
        login_record = LoginHistory.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=True
        )
        
        self.assertEqual(login_record.user, self.user)
        self.assertEqual(login_record.ip_address, '192.168.1.1')
        self.assertTrue(login_record.success)
        self.assertIsNone(login_record.logout_at)
    
    def test_login_history_str(self):
        """Test login history string representation"""
        login_record = LoginHistory.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=True
        )
        
        str_repr = str(login_record)
        self.assertIn('test@example.com', str_repr)
        self.assertIn('Success', str_repr)
    
    def test_failed_login_history(self):
        """Test failed login history"""
        login_record = LoginHistory.objects.create(
            user=self.user,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0',
            success=False,
            failure_reason='Invalid password'
        )
        
        self.assertFalse(login_record.success)
        self.assertEqual(login_record.failure_reason, 'Invalid password')
