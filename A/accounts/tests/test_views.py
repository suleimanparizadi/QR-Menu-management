from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import OTP_Code
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserRegisterViewTest(TestCase):
    """Tests for UserRegister view
    POST/accounts/register"""


    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:user_register')
        self.valid_data = {
            'phone_number': '09123456789',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure123',
            'password_confirm': 'secure123'
        }

    
    def test_register_with_valid_data(self):
        """Test registration create OTP and return success"""

        response = self.client.post(self.url, self.valid_data, format='json')

        #check response 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)


        #check the OPT was created
        otp_exist = OTP_Code.objects.filter(phone_number='09123456789').exists()
        self.assertTrue(otp_exist)


    def test_register_store_sessions_data(self):
        """Test sessions are stored correctly"""

        response = self.client.post(self.url, self.valid_data, format='json')

        sessions = self.client.session

        self.assertIn('user_register_session', sessions)
        self.assertEqual(sessions['user_register_session']['phone_number'],'09123456789')
        self.assertEqual(sessions['user_register_session']['username'], 'testuser')
        self.assertEqual(sessions['otp_send_count'],0)

 
    def test_register_returns_phone_last_four(self):
        """Test response includes last 4 digits of phone"""

        response = self.client.post(self.url, self.valid_data, format='json')
        
        self.assertIn('phone number', response.data)
        self.assertEqual(response.data['phone number'], '6789')

    
    def test_register_invalid_data_rejected(self):
        """Test invalid data returns 400"""
        invalid_data = {'phone_number':'1234'}

        response = self.client.post(self.url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



    def test_register_dose_not_created_yet(self):
        """Test to make sure the user NOT created while only the OTP sent"""

        response = self.client.post(self.url, self.valid_data, format='json')

        user_exist = User.objects.filter(phone_number='09123456789').exists()

        self.assertFalse(user_exist)



    def test_register_overwrite_previous_otp(self):
        """Test request OTP twice will overwrite previous one"""

        #first request
        self.client.post(self.url, self.valid_data, format='json')
        first_otp = OTP_Code.objects.get(phone_number='09123456789')
        print(f'===================={first_otp}')
        #second request
        self.client.post(self.url, self.valid_data, format='json')
        second_otp = OTP_Code.objects.get(phone_number='09123456789')
        print(f'===================={second_otp}')

        # counting otp's for the same phone number
        otp_count = OTP_Code.objects.filter(phone_number='09123456789').count()

        self.assertEqual(otp_count, 1)        




class VerifyUserPhoneTest(TestCase):
    """
    Tests for VerifyUserPhone view.
    POST /accounts/verify/
    """

    def setUp(self):
        self.client = APIClient()
        self.verify_url = reverse('accounts:verify_register')
        self.register_url = reverse('accounts:user_register')
        
        # First register to create session
        self.valid_data = {
            'phone_number': '09123456789',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure123',
            'password_confirm': 'secure123'
        }
        self.client.post(self.register_url, self.valid_data, format='json')

    

    def test_verify_correct_otp_create_user(self):
        """ztest the correct OTP will create a user"""

        otp = OTP_Code.objects.get(phone_number='09123456789')

        response = self.client.post(self.verify_url,
                                     {'code':str(otp.code)}
                                     , format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)


    
    def test_correct_otp_clear_sessions(self):
        """Test with correct OTP the sessions will get clear"""

        otp = OTP_Code.objects.get(phone_number='09123456789')

        response = self.client.post(self.verify_url,
                                     {'code':str(otp.code)},
                                       format='json')

        sessions = self.client.session
        self.assertNotIn('user_register_session', sessions)
        self.assertNotIn('otp_send_count', sessions)

        
    def test_wrong_otp_fails(self):
        """Test wrong OTP code return error"""


        response = self.client.post(self.verify_url,
                                     {'code':'000000'},
                                       format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data)

        # check if user created
        user_exist = User.objects.filter(phone_number='09123456789').exists()
        self.assertFalse(user_exist)



    def test_verify_without_session(self):
        """Test verification without any session stored"""

        #create a new API client(without session)
        new_client = APIClient()
        response = new_client.post(self.verify_url,
                                   {'code':'1234567'},
                                    format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('redirect', response.data)

        
       

    def test_verify_wrong_otp_keeps_sessions(self):

        response = self.client.post(
            self.verify_url,
            {'code':'000000'},
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(response.data['can_retry'])

        sessions = self.client.session
        self.assertIn('user_register_session', sessions)



    def test_verify_creates_user_with_correct_data(self):
        """Test created user has correct data from session"""
        otp = OTP_Code.objects.get(phone_number='09123456789')
        
        self.client.post(
            self.verify_url,
            {'code': str(otp.code)},
            format='json'
        )

        user = User.objects.get(phone_number='09123456789')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('secure123'))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_admin)


    def test_verify_returns_token(self):

        otp = OTP_Code.objects.get(phone_number='09123456789')
        
        response = self.client.post(
        self.verify_url,
        {'code': str(otp.code)},
        format='json')

        self.assertIn('token', response.data)
        self.assertIsNotNone(response.data['token'])


    
    def test_verify_returns_user_data(self):
        """Test successful verification returns user info"""
        otp = OTP_Code.objects.get(phone_number='09123456789')
        
        response = self.client.post(
            self.verify_url,
            {'code': str(otp.code)},
            format='json'
        )
        
        self.assertEqual(response.data['user']['username'], 'testuser')
        self.assertEqual(response.data['user']['phone_number'], '09123456789')




class UserLoginWithPasswordTest(TestCase):

    """Tests for UserLoginWithPassword view.
    POST /accounts/login_password/"""


    def setUp(self):

        self.client = APIClient()
        self.url = reverse('accounts:login_password')

        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='securepass123'
        )


    def test_login_success_token(self):
        """Test successful login return token with 200 sattus code"""


        response = self.client.post(self.url, {
            'identifier': 'testuser',
            'password':'securepass123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)


    def test_login_failure_return_401(self):
        """Test wrong paswword return 401"""

        response = self.client.post(self.url, {
            'identifier': 'testuser',
            'password':'wrongpassword'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    
    def test_deactivate_user_return_403(self):
        """Test deactivate user return 403"""

        self.user.is_active = False
        self.user.save()

        response = self.client.post(self.url, {
            'identifier': 'testuser',
            'password':'securepass123'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
                


    def test_invalid_input_return_400(self):
        """Test with invalid input return 400"""

        response = self.client.post(self.url, {
            
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    
    def test_token_remain_database_after_login(self):
        """Test token remain in data base after user logged in"""

        response = self.client.post(self.url, {
            'identifier': 'testuser',
            'password':'securepass123'
        }, format='json')

        token_exist = Token.objects.filter(user=self.user).exists()
        self.assertTrue(token_exist)




class UserLoginSendOTPTest(TestCase):
    """
        Tests for UserLoginWithOTP view (Send OTP step).
        POST /accounts/login/otp/send/
        """
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:login_otp_send')
        
        # Create a test user
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='securepass123')
        
    
    def test_send_otp_to_registered_user(self):

        response = self.client.post(self.url, {
            'phone_number': '09123456789'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check of the OTP created
        otp_exist = OTP_Code.objects.filter(phone_number='09123456789').exists()
        self.assertTrue(otp_exist)
        

    def test_send_otp_store_session(self):
        self.client.post(self.url,{
            'phone_number': '09123456789'
        },format='json')

        session = self.client.session

        self.assertEqual(session['login_phone'], '09123456789')
        self.assertEqual(session['otp_send_count'], 0)


    def test_unregistered_phone_same_response(self):
        """Test if unregistered phone number try to login return the same response """
        response = self.client.post(self.url, {
            'phone_number': '09999999999'
        }, format='json')

        #same status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        #same message
        self.assertIn('If this phone number is registered', response.data['detail'])


    def test_unregistered_phone_no_otp_created(self):
        """Test OTP NOT created for unregistered phone"""

        response = self.client.post(self.url, {
            'phone_number': '09999999999'
        }, format='json')

        otp_exist = OTP_Code.objects.filter(phone_number='09123456789').exists()
        self.assertFalse(otp_exist)
  

    def test_unregistered_phone_no_session_stored(self):
        """Test session NOT created for unregistered phone"""
        self.client.post(self.url, {
            'phone_number': '09999999999'
        }, format='json')

        session = self.client.session
        self.assertNotIn('login_phone', session)


    
    def test_invalid_phone_format(self):
        """Test invalid phone format returns 400"""
        response = self.client.post(self.url, {
            'phone_number': '12345'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_missing_phone(self):
        """Test missing phone field returns 400"""
        response = self.client.post(self.url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)




class UserLoginVerifyOTPTest(TestCase):
    """
    Tests for UserLoginVerifyOTP view (Verify OTP step).
    POST /accounts/login/otp/verify/
    """

    def setUp(self):
        self.client = APIClient()
        self.send_url = reverse('accounts:login_otp_send')
        self.verify_url = reverse('accounts:login_otp_verify')
        
        # Create a test user
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='securepass123'
        )
        
        # Request OTP to create session
        self.client.post(self.send_url, {
            'phone_number': '09123456789'
        }, format='json')
   


    def test_verify_correct_otp_returns_token(self):
        """Test correct OTP returns token and user data"""
        otp = OTP_Code.objects.get(phone_number='09123456789')
        
        response = self.client.post(self.verify_url, {
            'code': str(otp.code)
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')    
        


    def test_verify_clears_session_on_success(self):
        """Test session cleared after successful login"""
        otp = OTP_Code.objects.get(phone_number='09123456789')
        
        self.client.post(self.verify_url, {
            'code': str(otp.code)
        }, format='json')
        
        session = self.client.session
        self.assertNotIn('login_phone', session)



    def test_verify_wrong_code_returns_error(self):
        """Test wrong OTP code returns 400"""
        response = self.client.post(self.verify_url, {
            'code': '000000'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('detail', response.data) 



    def test_verify_wrong_code_keeps_session(self):
        """Test wrong code keeps session for retry"""
        self.client.post(self.verify_url, {
            'code': '000000'
        }, format='json')
        
        session = self.client.session
        self.assertIn('login_phone', session)



    def test_verify_expired_otp_clears_session(self):
        """Test expired OTP clears session"""
        from django.utils import timezone
        from datetime import timedelta
        
        # Make OTP expire
        OTP_Code.objects.filter(phone_number='09123456789').update(
            created_at=timezone.now() - timedelta(minutes=10)
        )

        otp = OTP_Code.objects.get(phone_number='09123456789')
        response = self.client.post(self.verify_url, {
            'code': str(otp.code)
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Session should be cleared
        session = self.client.session
        self.assertNotIn('login_phone', session)


    
    def test_verify_without_session_fails(self):
        """Test verification without prior OTP request fails"""
        new_client = APIClient()
        response = new_client.post(self.verify_url, {
            'code': '123456'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('sessions are expired', response.data['detail'].lower())


    def test_verify_deactivated_user_fails(self):
        """Test deactivated user cannot login"""
        self.user.is_active = False
        self.user.save()
        
        otp = OTP_Code.objects.get(phone_number='09123456789')
        response = self.client.post(self.verify_url, {
            'code': str(otp.code)
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('deactivated', response.data['detail'].lower())


    def test_verify_creates_token_in_database(self):
        """Test token is created in database after login"""
        otp = OTP_Code.objects.get(phone_number='09123456789')
        
        self.client.post(self.verify_url, {
            'code': str(otp.code)
        }, format='json')
        
        from rest_framework.authtoken.models import Token
        token_exists = Token.objects.filter(user=self.user).exists()
        self.assertTrue(token_exists)


    def test_verify_returns_user_data(self):
        """Test response includes correct user data"""
        otp = OTP_Code.objects.get(phone_number='09123456789')
        
        response = self.client.post(self.verify_url, {
            'code': str(otp.code)
        }, format='json')
        
        self.assertEqual(response.data['user']['phone_number'], '09123456789')
        self.assertEqual(response.data['user']['username'], 'testuser')   





class UserLogoutTest(TestCase):
    """
    Tests for UserLoggingOut view.
    POST /accounts/logout/
    """
     

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:logout')
        
        # Create user
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='securepass123'
        )    


    def _login(self):
        """Helper to login and get token"""
        login_url = reverse('accounts:login_password')
        response = self.client.post(login_url, {
            'identifier':'testuser',
            'password':'securepass123'
        }, format='json')
        return response.data['token']        
    
    def _authenticate(self):
        """Helper to authenticate client with token"""
        token = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
                    

    
    def test_loggout_deleted_token(self):
        """Test if the logout delete the token"""

        self._authenticate()

        # login
        token_exist = Token.objects.filter(user=self.user).exists()
        self.assertTrue(token_exist)

        #logout
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token_exist = Token.objects.filter(user=self.user).exists()
        self.assertFalse(token_exist)


    def test_logout_returns_success_message(self):
        """Test logout returns success detail"""
        self._authenticate()
        
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
       

    def test_logout_without_authentication_fails(self):
        """Test unauthenticated request returns 401"""
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
class UserProfileViewTest(TestCase):
    """
    Tests for UserProfileView.
    GET /accounts/profile_view/{pk}/
    """

    def setUp(self):
        self.client = APIClient()
        
        # Create users
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            email='test@example.com',
            password='securepass123'
        )

        self.other_user = User.objects.create_user(
            phone_number='09222222222',
            username='otheruser',
            email='other@example.com',
            password='pass123'
        )  
    


    def _login(self, username='testuser', password='securepass123'):
        """Helper to login and get token"""
        login_url = reverse('accounts:login_password')
        response = self.client.post(login_url, {
            'identifier': username,
            'password': password
        }, format='json')
        return response.data['token']
    

    def _authenticate(self, username='testuser', password='securepass123'):
        """Helper to authenticate client"""
        token = self._login(username, password)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')



    def test_view_own_profile(self):
        """Test authenticated user can view own profile"""
        self._authenticate()
        
        url = reverse('accounts:profile_view')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['phone_number'], '09123456789')
        self.assertEqual(response.data['email'], 'test@example.com')


    def test_unauthenticated_cannot_view_profile(self):
        """Test unauthenticated request returns 401"""
        url = reverse('accounts:profile_view')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        


class ResendOTPViewTest(TestCase):

    """
    Tests for ResendOTPView.
    POST /accounts/otp/resend/
    Works for registration, login, and phone change flows.
    """

    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:otp_resend')

    
    def test_resend_otp_registration(self):
        
        
        register_url = reverse('accounts:user_register')
        self.client.post(register_url, {
            'phone_number': '09123456789',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure123',
            'password_confirm': 'secure123'
        }, format='json')
        
        original_otp = OTP_Code.objects.get(phone_number='09123456789')

        # Resend OTP 
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('New OTP sent', response.data['detail'])

        new_otp = OTP_Code.objects.get(phone_number='09123456789')
        self.assertNotEqual(original_otp.code, new_otp.code)



    def test_resend_otp_for_login(self):
        """Test resend OTP works for login flow"""
        # Create user first
        User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='secure123'
        )
        
        # Request login OTP
        login_otp_url = reverse('accounts:login_otp_send')
        self.client.post(login_otp_url, {
            'phone_number': '09123456789'
        }, format='json')

        original_otp = OTP_Code.objects.get(phone_number='09123456789')
        
        # Resend OTP
        response = self.client.post(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check OTP updated
        new_otp = OTP_Code.objects.get(phone_number='09123456789')
        self.assertNotEqual(new_otp.code, original_otp.code)        



    def test_resend_otp_returns_attempt_left(self):
        """Test response shows remaining attempts"""

        register_url = reverse('accounts:user_register')
        self.client.post(register_url,{
            'phone_number': '09123456789',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure123',
            'password_confirm': 'secure123'
        }, format='json')


        response = self.client.post(self.url)

        self.assertIn('attempts left', response.data)
        self.assertEqual(response.data['attempts left'], 2)  
        
    
    def test_resend_without_session(self):
        """Test resend without any prior OTP request"""

        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('No active OTP request', response.data['detail'])


    def test_resend_increments_counter(self):
        """Test counter increases with each resend"""

        register_url = reverse('accounts:user_register')
        self.client.post(register_url, {
            'phone_number': '09123456789',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure123',
            'password_confirm': 'secure123'
        }, format='json')    

        #first request
        self.client.post(self.url)
        session = self.client.session
        self.assertEqual(session['otp_send_count'], 1)

        # second request
        self.client.post(self.url)
        session = self.client.session
        self.assertEqual(session['otp_send_count'], 2)
               
            
    def test_too_many_resends_blocked(self):
        """Test blocked after 3 resends"""

        register_url = reverse('accounts:user_register')
        self.client.post(register_url, {
            'phone_number': '09123456789',
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'secure123',
            'password_confirm': 'secure123'
        }, format='json')    


        # 3 request for OTP
        self.client.post(self.url)
        self.client.post(self.url)
        self.client.post(self.url)

        # 4th request
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertIn('Too many', response.data['detail'])


class RequestChangingPhoneNUmberTest(TestCase):
    """
    Tests for RequestChangingPhoneNumber view.
    POST /accounts/profile/phone/request/
    """


    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:changing_number')
        
        # Create and authenticate user
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='securepass123'
        )
        self._authenticate()


    def _authenticate(self):
        """Helper to login and set token"""
        login_url = reverse('accounts:login_password')
        response = self.client.post(login_url, {
            'identifier': 'testuser',
            'password': 'securepass123'
        }, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}') 


    def test_request_phone_change_sends_otp(self):
        """Test OTP sent to new phone number"""
        response = self.client.post(self.url, {
            'new_phone_number': '09333333333'
        }, format='json')    


        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check OTP created for NEW phone
        otp_exists = OTP_Code.objects.filter(phone_number='09333333333').exists()
        self.assertTrue(otp_exists)


    def test_request_phone_change_stores_session(self):
        """Test new phone stored in session"""
        self.client.post(self.url, {
            'new_phone_number': '09333333333'
        }, format='json')
        
        session = self.client.session
        self.assertEqual(session['new_phone_number'], '09333333333')
        self.assertEqual(session['otp_send_count'], 0)


    def test_request_duplicate_phone_rejected(self):
        """Test cannot request phone that's already registered"""
        # Create another user with that phone
        User.objects.create_user(
            phone_number='09333333333',
            username='otheruser',
            password='pass123'
        )

        response = self.client.post(self.url, {
            'new_phone_number': '09333333333'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_request_unauthenticated_fails(self):
        """Test unauthenticated request returns 401"""
        # Create new client without auth
        new_client = APIClient()
        response = new_client.post(self.url, {
            'new_phone_number': '09333333333'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)                        



class ConfirmPhoneUpdateViewTest(TestCase):
    """
    Tests for ConfirmPhoneUpdateView.
    POST /accounts/profile/phone/confirm/
    """

    def setUp(self):
        self.client = APIClient()
        self.request_url = reverse('accounts:changing_number')
        self.confirm_url = reverse('accounts:phone_change_confirm')
        
        # Create and authenticate user
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='securepass123'
        )
        self._authenticate()   


    def _authenticate(self):
        """Helper to login and set token"""
        
        login_url = reverse('accounts:login_password')
        response = self.client.post(login_url, {
            'identifier': 'testuser',
            'password': 'securepass123'
        }, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')   



    def _request_phone_change(self, new_phone='09333333333'):
        """Helper to request phone change (creates session + OTP)"""

        self.client.post(self.request_url, {
            'new_phone_number': new_phone
        }, format='json')  



    def test_confirm_phone_change_success(self):
        """Test successful phone number update"""

        self._request_phone_change()
        
        otp = OTP_Code.objects.get(phone_number='09333333333')
        
        response = self.client.post(self.confirm_url, {
            'code': str(otp.code)
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
       
       # Check phone was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '09333333333')



    def test_confirm_phone_clears_session(self):
        """Test session cleared after successful update"""

        self._request_phone_change()
        
        otp = OTP_Code.objects.get(phone_number='09333333333')
        self.client.post(self.confirm_url, {
            'code': str(otp.code)
        }, format='json')
        
        session = self.client.session
        self.assertNotIn('new_phone_number', session)
        self.assertNotIn('otp_send_count', session)



    def test_confirm_wrong_otp_fails(self):
        """Test wrong OTP code returns error"""

        self._request_phone_change()
        
        response = self.client.post(self.confirm_url, {
            'code': '000000'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Phone should NOT be changed
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, '09123456789')


    def test_confirm_wrong_otp_keeps_session(self):
        """Test wrong code keeps session for retry"""

        self._request_phone_change()
        
        self.client.post(self.confirm_url, {
            'code': '000000'
        }, format='json')
        
        session = self.client.session
        self.assertIn('new_phone_number', session)



    def test_confirm_without_session_fails(self):
        """Test confirmation without prior request fails"""

        response = self.client.post(self.confirm_url, {
            'code': '123456'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Session expired', response.data['detail'])


    def test_confirm_unauthenticated_fails(self):
        """Test unauthenticated request returns 401"""
        new_client = APIClient()
        response = new_client.post(self.confirm_url, {
            'code': '123456'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class CancelPhoneChangeView(TestCase):
    """
    Tests for CancelPhoneChangeView.
    POST /accounts/profile/change_number/cancel/
    """


    def setUp(self):
        self.client = APIClient()
        self.request_url = reverse('accounts:changing_number')
        self.cancel_url = reverse('accounts:cancel_phone_change')
        
        # Create and authenticate user
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='securepass123'
        )   

        self._authenticate()


    def _authenticate(self):
        """Helper to login and set token"""
        login_url = reverse('accounts:login_password')
        response = self.client.post(login_url, {
            'identifier': 'testuser',
            'password': 'securepass123'
        }, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')




    def _request_phone_change(self):
        """Helper to create a pending phone change"""
        self.client.post(self.request_url, {
            'new_phone_number': '09333333333'
        }, format='json'  )



    def test_cancel_clears_phone_session(self):

        """Test cancel removes new phone from session"""
        self._request_phone_change()
        
        # Verify session exists
        session = self.client.session
        self.assertIn('new_phone_number', session)
        
        # Cancel
        response = self.client.post(self.cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify session cleared
        session = self.client.session
        self.assertNotIn('new_phone_number', session)


    def test_cancel_clears_otp_count(self):
        """Test cancel removes otp_send_count from session"""
        self._request_phone_change()
        
        session = self.client.session
        self.assertIn('otp_send_count', session)
        
        self.client.post(self.cancel_url)
        
        session = self.client.session
        self.assertNotIn('otp_send_count', session)  


    def test_cancel_returns_success_message(self):
        """Test cancel returns success detail"""
        self._request_phone_change()
        
        response = self.client.post(self.cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIn('cancelled', response.data['detail'].lower())   


    def test_cancel_then_request_new_change(self):
        """Test can request new phone change after cancel"""
        # First request
        self._request_phone_change()
        
        # Cancel it
        self.client.post(self.cancel_url)
        
        # Request again
        response = self.client.post(self.request_url, {
            'new_phone_number': '09444444444'
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        session = self.client.session
        self.assertEqual(session['new_phone_number'], '09444444444') 

    def test_cancel_unauthenticated_fails(self):
        """Test unauthenticated request returns 401"""
        new_client = APIClient()
        response = new_client.post(self.cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)               



# accounts/tests/test_views.py (add to existing file)

class UsernameChangeViewTest(TestCase):
    """
    Tests for UsernameChangeView.
    PUT /accounts/profile/username/
    """
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('accounts:change_username')
        
        # Create users
        self.user = User.objects.create_user(
            phone_number='09123456789',
            username='testuser',
            password='securepass123'
        )
        
        self.other_user = User.objects.create_user(
            phone_number='09222222222',
            username='otheruser',
            password='pass123'
        )
        
        self._authenticate()
    
    def _authenticate(self):
        """Helper to login and set token"""
        login_url = reverse('accounts:login_password')
        response = self.client.post(login_url, {
            'identifier': 'testuser',
            'password': 'securepass123'
        }, format='json')
        token = response.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')


    def test_change_username_success(self):
        """Test successful username update"""

        response = self.client.put(self.url, {
            'username': 'newname'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
        self.assertIn('successfully', response.data['detail'].lower())
    

    def test_change_username_updates_database(self):
        """Test username actually changed in database"""

        self.client.put(self.url, {
            'username': 'newname'
        }, format='json')
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, 'newname')
    


    def test_change_username_returns_updated_data(self):
        """Test response includes updated username"""

        response = self.client.put(self.url, {
            'username': 'newname'
        }, format='json')
        
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['username'], 'newname')
    


    
    def test_change_username_same_username_allowed(self):
        """Test keeping the same username works"""

        response = self.client.put(self.url, {
            'username': 'testuser'  # Same as current
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    


    def test_change_username_unauthenticated_fails(self):
        """Test unauthenticated request returns 401"""
        
        new_client = APIClient()
        response = new_client.put(self.url, {
            'username': 'newname'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)