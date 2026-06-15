from django.test import TestCase
from rest_framework import serializers
from django.contrib.auth import get_user_model
from accounts import serializer
from accounts.models import OTP_Code

User = get_user_model()


class UserRegisterSerializerTest(TestCase):

    def setUp(self):
        
        self.valid_data= {
            'phone_number':'09123456789',
            'username':'testuser',
            'email':'testexample@email.com',
            'password':'secure1234',
            'password_confirm':'secure1234'
        }

    def test_valid_data(self):

        serial_data = serializer.UserRegisterSerializer(data=self.valid_data)

        self.assertTrue(serial_data.is_valid())

    
    def test_password_confirm(self):

        self.valid_data['password_confirm'] = 'different'
        serila_data = serializer.UserRegisterSerializer(data=self.valid_data)

        self.assertFalse(serila_data.is_valid())
        self.assertIn('password_confirm', serila_data.errors)

    
    def test_password_too_short(self):
        self.valid_data['password'] = '123'
        self.valid_data['password_confirm'] = '123'

        serial_data = serializer.UserRegisterSerializer(data=self.valid_data)

        self.assertFalse(serial_data.is_valid())



    def test_missing_requeird_fields(self):

        serial_data = serializer.UserRegisterSerializer(data={})

        self.assertFalse(serial_data.is_valid())
        self.assertIn('phone_number', serial_data.errors)
        self.assertIn('username', serial_data.errors)
        self.assertIn('password', serial_data.errors)


    def test_password_is_write_only(self):
        """Test password not in serialized output"""

        user = User.objects.create_user(
            phone_number = '09123456789',
            username='testuser',
            password='secure1234'
        )

        serial_data = serializer.UserRegisterSerializer(instance=user)
        self.assertNotIn('password', serial_data)



    def test_create_user(self):

        """Testing if actually creating a user
        is_valid() must be called before save() method! 
        """

        serial_data = serializer.UserRegisterSerializer(data=self.valid_data)
        self.assertTrue(serial_data.is_valid())

        user = serial_data.save()

        self.assertEqual(user.phone_number, '09123456789')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('secure1234'))
        self.assertFalse(user.is_admin)



    def test_phone_number_unique(self):
        """Testing duplicate phone number rejected"""

        User.objects.create_user(
            phone_number='09123456789',
            username='existing',
            password='pass123'
        )

        serial_data = serializer.UserRegisterSerializer(data = self.valid_data)

        self.assertFalse(serial_data.is_valid())
        self.assertIn('phone_number', serial_data.errors)




class LoginWithPasswordTest(TestCase):

    def test_valid_data(self):

        data = {'identifier': 'testuser', 'password': 'secure123'}
        serial_data = serializer.UserLoginWithPasswordSerializer(data=data)
        self.assertTrue(serial_data.is_valid())

    
    def test_invalid_data(self):

        data = {}
        serial_data = serializer.UserLoginWithPasswordSerializer(data=data)
        self.assertFalse(serial_data.is_valid())
        self.assertIn('identifier', serial_data.errors)
        self.assertIn('password',serial_data.errors)

    

class LoginSendOTPSerializerTest(TestCase):


    def test_valid_phone_number(self):
        """Test valid phone format"""
        data = {'phone_number':'09123456789'}
        serial_data = serializer.UserLoginSendOTPSerializer(data=data)
        self.assertTrue(serial_data.is_valid())

    def test_invalid_phone_wrong_prefix(self):
        """Test phone not starting with 09"""
        data = {'phone_number': '08123456789'}
        serial_data = serializer.UserLoginSendOTPSerializer(data=data)
        self.assertFalse(serial_data.is_valid())
    
    def test_invalid_phone_too_short(self):
        """Test phone too short"""
        data = {'phone_number': '0912345678'}
        serial_data = serializer.UserLoginSendOTPSerializer(data=data)
        self.assertFalse(serial_data.is_valid())

    def test_invalid_phone_too_long(self):
        """Test phone too long"""
        data = {'phone_number': '091234567890'}
        serial_data = serializer.UserLoginSendOTPSerializer(data=data)
        self.assertFalse(serial_data.is_valid())
    
    def test_invalid_phone_letters(self):
        """Test phone with letters"""
        data = {'phone_number': 'abcdefghijk'}
        serial_data = serializer.UserLoginSendOTPSerializer(data=data)
        self.assertFalse(serial_data.is_valid())

    def test_missing_phone(self):
        """Test missing phone field"""
        data = {}
        serial_data = serializer.UserLoginSendOTPSerializer(data=data)
        self.assertFalse(serial_data.is_valid())

  

class ConfirmOTPCodeTest(TestCase):
    def test_valid_code(self):
        """Test valid numeric code"""
        data = {'code': '123456'}
        serial_data = serializer.UserConfirmOTPCode(data=data)
        self.assertTrue(serial_data.is_valid())
    
    def test_empty_code(self):
        """Test empty code"""
        data = {'code': ''}
        serial_data = serializer.UserConfirmOTPCode(data=data)
        self.assertFalse(serial_data.is_valid())

    def test_missing_code(self):
        """Test missing code field"""
        data = {}
        serial_data = serializer.UserConfirmOTPCode(data=data)
        self.assertFalse(serial_data.is_valid())



class UserProfileSerializerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            email='test@example.com',
            password='secure123'
        )


    def test_profile_fields(self):
        """Test correct fields are returned"""
        serial_data = serializer.UserProfileSerializer(self.user)
        data = serial_data.data
        
        self.assertIn('username', data)
        self.assertIn('phone_number', data)
        self.assertIn('email', data)
        self.assertIn('created_at', data)
        
        self.assertEqual(data['username'], 'testuser')
        self.assertEqual(data['phone_number'], '09123456789')


    def test_password_not_exposed(self):
        """Test password is not in profile data"""
        serial_data = serializer.UserProfileSerializer(self.user)
        self.assertNotIn('password', serial_data.data)



class UserUpdateUsernameSeriloaizerTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
        phone_number='09123456789',
        username='testuser',
        password='secure123'
    )
        self.other_user = User.objects.create_user(
        phone_number='09222222222',
        username='otheruser',
        password='pass123'
    )


    def test_valid_username_update(self):
        """Test updating to a new valid username"""
        serial_data = serializer.UserUpdateUsernameSerializer(
            instance=self.user,
            data={'username': 'newname'}
        )
        self.assertTrue(serial_data.is_valid())


    def test_duplicate_username_rejected(self):
        """Test can't take another user's username"""
        serial_data = serializer.UserUpdateUsernameSerializer(
            instance=self.user,
            data={'username': 'otheruser'}  # Taken by other_user
        )
        self.assertFalse(serial_data.is_valid())
        self.assertIn('username', serial_data.errors)


    def test_same_username_allowed(self):
        """Test user can keep their own username"""
        serial_data = serializer.UserUpdateUsernameSerializer(
            instance=self.user,
            data={'username': 'testuser'}  # Same as current
        )
        self.assertTrue(serial_data.is_valid())

   

    def test_update_saves_username(self):
        """Test update actually changes username"""
        serial_data = serializer.UserUpdateUsernameSerializer(
            instance=self.user,
            data={'username': 'updatedname'}
        )
        self.assertTrue(serial_data.is_valid())
        updated_user = serial_data.save()
        
        self.assertEqual(updated_user.username, 'updatedname')
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'updatedname')


    def test_empty_username(self):
        """Test empty username rejected"""
        serial_data = serializer.UserUpdateUsernameSerializer(
            instance=self.user,
            data={'username': ''}
        )
        self.assertFalse(serial_data.is_valid())


class UserUpdatePhoneNumberTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='secure123'
        )
        User.objects.create_user(
            phone_number='09222222222',
            username='otheruser',
            password='pass123')
        
    def test_valid_new_phone(self):
        """Test valid new phone number"""
        data = {'new_phone_number': '09333333333'}
        serial_data = serializer.UserUpdatePhoneNumber(data=data)
        self.assertTrue(serial_data.is_valid())
    
    def test_duplicate_phone_rejected(self):
        """Test can't use already registered phone"""
        data = {'new_phone_number': '09222222222'}  # Taken
        serial_data = serializer.UserUpdatePhoneNumber(data=data)
        self.assertFalse(serial_data.is_valid())
        self.assertIn('new_phone_number', serial_data.errors)

    
    def test_invalid_phone_format(self):
        """Test invalid phone format"""
        data = {'new_phone_number': '12345'}
        serial_data = serializer.UserUpdatePhoneNumber(data=data)
        self.assertFalse(serial_data.is_valid())