from accounts.models import OTP_Code
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import timedelta
from django.test import TestCase
from django.contrib.auth import get_user_model


User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):

        self.data ={
            'phone_number':'09123456789',
            'username':'testuser',
            'email':'testuseremal@example.com',
            'password':'securepassword1234'
        }

    def test_user_creation(self):
        user = User.objects.create_user(
            phone_number=self.data['phone_number'],
            username = self.data['username'],
            email = self.data['email'],
            password = self.data['password']
        )
 

        self.assertEqual(user.username, self.data['username'])
        self.assertEqual(user.phone_number, self.data['phone_number'])
        self.assertEqual(user.email, self.data['email'])
        self.assertTrue(user.check_password, self.data['password'])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)
        self.assertFalse(user.is_superuser)

    
    def test_missing_username(self):

        with self.assertRaises(ValidationError):
            User.objects.create_user(
                username=None,
                phone_number=self.data['phone_number'],
                password=self.data['password']
            )


    def test_missing_phone_number(self):

        with self.assertRaises(ValidationError):
            User.objects.create_user(
                username=self.data['username'],
                phone_number=None,
                password=self.data['password']
            )

    
    def test_email_optional(self):
        
        user = User.objects.create_user(
            username=self.data['username'],
            phone_number=self.data['phone_number'],
            password=self.data['password'],
            email=None,   
        )

        self.assertIsNone(user.email)


# Super user tests


    def test_create_superuser(self):
        super_user = User.objects.create_superuser(
            username=self.data['username'],
            phone_number=self.data['phone_number'],
            password=self.data['password']
        )

        self.assertEqual(super_user.username, self.data['username']),
        self.assertEqual(super_user.phone_number, self.data['phone_number']),
        self.assertTrue(super_user.check_password, self.data['password']),
        self.assertTrue(super_user.is_active),
        self.assertTrue(super_user.is_superuser),
        self.assertTrue(super_user.is_admin),


   
    def test_missing_superuser_username(self):

        with self.assertRaises(ValidationError):
            User.objects.create_superuser(
                username=None,
                phone_number=self.data['phone_number'],
                password=self.data['password']
            )


    def test_missing_superuser_phone_number(self):

        with self.assertRaises(ValidationError):
            User.objects.create_superuser(
                username=self.data['username'],
                phone_number=None,
                password=self.data['password']
            )




