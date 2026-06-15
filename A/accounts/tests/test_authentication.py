from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from accounts.models import OTP_Code
from accounts.authentication import IdentifierAuthentication
from accounts.otp_authentication import OTPAuthentication


User = get_user_model()



class IdentifierAuthenticationTest(TestCase):

    """Testing password-base Authentication."""

    def setUp(self):
        self.backend = IdentifierAuthentication()
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            phone_number = '09123456789',
            username = 'testuser',
            password = 'secure1234'
        )

    
    def test_authentication_with_password(self):
        """Test login with password"""

        request = self.factory.post('/login/')
        user = self.backend.authenticate(
            request, 
            identifier='testuser',
            password='secure1234'
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')


    
    def test_authentication_with_phone(self):
        """Test login with phone number"""

        request = self.factory.post('/login/')
        user = self.backend.authenticate(
            request, 
            identifier='09123456789',
            password='secure1234'
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.phone_number, '09123456789')


    def test_authenticate_with_wrong_password(self):
        """Test login with wrong password"""

        request = self.factory.post('/login/')
        user = self.backend.authenticate(
            request,
            identifier='09123456789',
            password='wrong_password'
        )

        self.assertIsNone(user)



    def test_authenticate_with_missing_identifier(self):
        """Test None identifier, return none."""

        request = self.factory.post('/login/')
        user = self.backend.authenticate(
            request,
            identifier=None,
            password='secure1234'
        )

        self.assertIsNone(user)



    def test_authenticate_with_missing_password(self):
        """Test None password, return none."""

        request = self.factory.post('/login/')
        user = self.backend.authenticate(
            request,
            identifier='testuser',
            password=None
        )

        self.assertIsNone(user)



    def test_get_user_valid(self):
        """Test get_user with valid ID"""

        user = self.backend.get_user(self.user.pk)
        self.assertIsNotNone(user)




    def test_get_user_valid(self):
        """Test not get_user with invalid ID"""

        user = self.backend.get_user(999999)
        self.assertIsNone(user)




class OTPAthentcationTest(TestCase):

    def setUp(self):
        self.backend = OTPAuthentication()
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            phone_number = '09123456789',
            username = 'testuser',
            password = 'secure1234'
        )


    def test_authenticate_valid_otp_returns_user(self):
        """Test valid otp returns the correct user"""

        OTP_Code.objects.create(phone_number='09123456789', code=123456)
        
        request = self.factory.post('/login/otp/')
        user = self.backend.authenticate(
            request,
            phone_number = '09123456789',
            otp_code='123456'
        )

        self.assertIsNotNone(user)
        self.assertEqual(user.phone_number, '09123456789')



    def test_authenticate_valid_otp_delete_otp(self):
        """Test the otp code will be deleted after successful login"""
        OTP_Code.objects.create(phone_number='09123456789', code=123456)

        request = self.factory.post('/login/otp/')
        user = self.backend.authenticate(
            request,
            phone_number='09123456789',
            otp_code='123456'
        )

        exist = OTP_Code.objects.filter(phone_number='09123466789').exists()

        self.assertFalse(exist)


    def test_authentication_with_invalid_otp(self):
        """Testing login with incorrect OTP"""

        OTP_Code.objects.create(phone_number='09123456789', code=123456)

        request = self.factory.post('/login/otp/')

        user = self.backend.authenticate(
            request,
            phone_number='09123456789',
            otp_code='000000'
        )

        self.assertIsNone(user)

    
    def test_authenticate_user_not_found(self):
        """Test valid OTP but no user with that phone number"""

        OTP_Code.objects.create(phone_number='09111111111', code=123456)

        request = self.factory.post('/login/otp/')

        user = self.backend.authenticate(
            request,
            phone_number='09111111111',
            otp_code='123456'
        )

        self.assertIsNone(user)

    

    def test_authenticate_inactive_user(self):
        """Test inactive user cannot login with valid OTP"""

        self.user.is_active = False
        self.user.save()

        OTP_Code.objects.create(phone_number='09111111111', code=123456)

        request = self.factory.post('/login/otp/')

        user = self.backend.authenticate(
            request,
            phone_number='09111111111',
            otp_code='123456'
        )

        self.assertIsNone(user)

    

    def test_authenticate_missing_phone(self):
        """Test None phone, return None"""

        request = self.factory.post('/login/otp/')

        user = self.backend.authenticate(
            request,
            phone_number=None,
            otp_code='123456'
        )

        self.assertIsNone(user)




    def test_authenticate_missing_otp(self):
        """Test no phone, return None"""

        request = self.factory.post('/login/otp/')

        user = self.backend.authenticate(
            request,
            phone_number='09123456789',
            otp_code=None
        )

        self.assertIsNone(user)

    
    def test_get_user_valid(self):
        """Test get user with valid ID"""

        user = self.backend.get_user(self.user.pk)

        self.assertIsNotNone(user)


    
    def test_get_user_valid(self):
        """Test get user with valid ID"""

        user = self.backend.get_user(999999)

        self.assertIsNone(user)

