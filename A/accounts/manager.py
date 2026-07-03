from django.contrib.auth.models import BaseUserManager
from django.core.exceptions import ValidationError
import re


class User_manager(BaseUserManager):
    

    def _create_user(self, phone_number, username, email=None, password=None, **extra_fields):

        """
        A blue print to create normal user or super users
        """


        if not phone_number:
            raise ValidationError("phone number is required")
        
        if not username:
            raise ValidationError("Username is required")
        

        phone_number = self._normalize_phone(phone_number)
        email = self.normalize_email(email) if email else None

        user = self.model(
            phone_number = phone_number,
            username = username,
            email = email,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)
        return user
    



    def create_user(self,  phone_number, username, email=None, password=None, **extra_fields):
        """
        create a normal user
        """
        extra_fields.setdefault('is_admin', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_active', True)

        return self._create_user(
            phone_number=phone_number,
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
    
    def create_superuser(self,  phone_number, username, email=None, password=None, **extra_fields):
        """
        create a super user
        """
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_admin') is not True:
            raise ValidationError("Super user must be admin!")
        
        if extra_fields.get('is_superuser') is not True:
            raise ValidationError("Super user must have is_superuser=True.")

        return self._create_user(
            phone_number=phone_number,
            username=username,
            email=email,
            password=password,
            **extra_fields
        )
    

    def _normalize_phone(self, phone):
        """
        remove non-digits chrachters to save validated phone number
        """

        if phone is None:
            return None
        
        phone = re.sub(r'\D', '', str(phone))

        if len(phone) != 11:
            raise ValidationError("Phone number must have exactly 11 digits")
        
        return phone


    def active(self):

        return self.get_queryset().filter(is_active=True)


    def admin(self):

        return self.get_queryset().filter(is_admin=True)

