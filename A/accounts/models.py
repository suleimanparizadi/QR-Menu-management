from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from .manager import User_manager
from datetime import timedelta
from django.utils import timezone


class User(AbstractBaseUser, PermissionsMixin):

    """
    custom user model with phone number as a primary identifier
    """

    phone_number = models.CharField(
        max_length=11,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'09\d{9}$',
                message="phone number must be in format: 09xxxxxxxxx"
            )
        ]
    )

    username = models.CharField(
        max_length=128,
        unique=True

    )

    email = models.EmailField(
        max_length=125,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(
        default=True
    )

    is_admin = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    objects = User_manager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['username', 'email']


    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        indexes = [
            # index create a B-Tree data structure for performenc 
            models.Index(fields=['phone_number']),
            models.Index(fields=['username']),
            models.Index(fields=['email'])
        ]

    def __str__(self):
        return f"{self.phone_number} - {self.username}"
    
    @property
    def is_staff(self):
        return self.is_admin
    

    def deactivate(self):
        self.is_active = False
        self.save(update_fields=['is_active'])

    def activate(self):
        self.is_active = True
        self.save(update_fields=['is_active'])
     


class OTP_Code(models.Model):

    """
    for store and deleting the opt code 
    """

    phone_number = models.CharField(max_length=11, unique=True)
    code = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)

    EXPIRY_MINUTES = 5

    def is_expired(self):
        """
        to check if the code is expired or not
        """
        expiry_time = self.created_at + timedelta(minutes=self.EXPIRY_MINUTES)
        result = timezone.now() > expiry_time
        return result
    def __str__(self):
        return f"{self.phone_number} - {self.code}"



