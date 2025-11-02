"""
User and authentication models
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.validators import EmailValidator
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Custom user manager for User model
    """
    
    def create_user(self, email, username, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        if not username:
            raise ValueError('The Username field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, username, password=None, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, username, password, **extra_fields)


class UserRole(models.TextChoices):
    """User role choices"""
    ADMIN = 'admin', 'Administrator'
    SUPERVISOR = 'supervisor', 'Supervisor'
    OPERATOR = 'operator', 'Operator'
    AUDITOR = 'auditor', 'Auditor'


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model with email as the unique identifier
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    email = models.EmailField(
        max_length=255,
        unique=True,
        db_index=True,
        validators=[EmailValidator(message='Enter a valid email address')]
    )
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    
    # Role and status
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.OPERATOR,
        db_index=True
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Additional fields
    phone = models.CharField(max_length=20, blank=True, null=True)
    dni = models.CharField(max_length=8, unique=True, null=True, blank=True, db_index=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Security
    failed_login_attempts = models.IntegerField(default=0)
    account_locked_until = models.DateTimeField(null=True, blank=True)
    password_changed_at = models.DateTimeField(default=timezone.now)
    must_change_password = models.BooleanField(default=False)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email', 'is_active']),
            models.Index(fields=['username', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
    
    def get_full_name(self):
        """Return the user's full name."""
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username
    
    def get_short_name(self):
        """Return the user's short name."""
        return self.first_name or self.username
    
    def is_account_locked(self):
        """Check if account is currently locked."""
        if self.account_locked_until:
            if timezone.now() < self.account_locked_until:
                return True
            else:
                # Unlock account if lock period has expired
                self.account_locked_until = None
                self.failed_login_attempts = 0
                self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
        return False
    
    def lock_account(self, duration_minutes=30):
        """Lock the user account for specified duration."""
        self.account_locked_until = timezone.now() + timezone.timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def increment_failed_login(self, max_attempts=5, lock_duration=30):
        """
        Increment failed login attempts and lock account if threshold is reached.
        """
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= max_attempts:
            self.lock_account(duration_minutes=lock_duration)
        self.save(update_fields=['failed_login_attempts'])
    
    def reset_failed_login(self):
        """Reset failed login attempts counter."""
        self.failed_login_attempts = 0
        self.save(update_fields=['failed_login_attempts'])
    
    def has_role(self, *roles):
        """Check if user has any of the specified roles."""
        return self.role in roles
    
    def is_admin(self):
        """Check if user is an administrator."""
        return self.role == UserRole.ADMIN or self.is_superuser
    
    def is_supervisor(self):
        """Check if user is a supervisor or higher."""
        return self.role in [UserRole.ADMIN, UserRole.SUPERVISOR] or self.is_superuser
    
    def is_operator(self):
        """Check if user is an operator or higher."""
        return self.role in [UserRole.ADMIN, UserRole.SUPERVISOR, UserRole.OPERATOR] or self.is_superuser


class LoginHistory(models.Model):
    """
    Track user login history for security auditing
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_history')
    
    # Login details
    login_at = models.DateTimeField(default=timezone.now, db_index=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    
    # Request details
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    
    # Status
    success = models.BooleanField(default=True)
    failure_reason = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'login_history'
        verbose_name = 'Login History'
        verbose_name_plural = 'Login Histories'
        ordering = ['-login_at']
        indexes = [
            models.Index(fields=['user', '-login_at']),
            models.Index(fields=['ip_address', '-login_at']),
        ]
    
    def __str__(self):
        status = 'Success' if self.success else f'Failed ({self.failure_reason})'
        return f"{self.user.email} - {self.login_at} - {status}"
