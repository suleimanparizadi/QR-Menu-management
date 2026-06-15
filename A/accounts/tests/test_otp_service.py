from django.test import TestCase
from utils.otp_service import OTP_Service
from accounts.models import OTP_Code
from django.utils import timezone
from datetime import timedelta




class TestOTPService(TestCase):

    def setUp(self):
        self.phone_number = '09123456789'
        self.otp_service = OTP_Service(self.phone_number)
        


    def test_integer_code(self):

        code = self.otp_service.generate_code()
        self.assertIsInstance(code, int)

    
    def test_6digits_code(self):
        code = self.otp_service.generate_code()
        self.assertGreaterEqual(code, 100000)
        self.assertLessEqual(code, 999999)

    def test_create_code(self):

        self.otp_service.create_otp()
        otp_exist = OTP_Code.objects.filter(
            phone_number=self.phone_number
                                        ).exists()
        
        self.assertTrue(otp_exist)

    
    def test_create_otp_update_otp(self):
        """Test update_or_create updates existing OTP instead creating duplicate"""

        self.otp_service.create_otp()
        first_otp = OTP_Code.objects.get(phone_number=self.phone_number)

        import time 
        time.sleep(0.5)
        self.otp_service.create_otp()

        otp_count = OTP_Code.objects.filter(phone_number=self.phone_number).count()

        self.assertEqual(otp_count, 1)

        updated_otp = OTP_Code.objects.get(phone_number=self.phone_number)
        self.assertNotEqual(first_otp.code, updated_otp.code)

    



# ======Verify code tests==================================


    def test_verify_correct_code(self):
        """Test verification with correct code"""

        code = self.otp_service.create_otp()

        is_valid, message = self.otp_service.verify_code(str(code))

        self.assertTrue(is_valid)
        self.assertIn('success', message.lower())


    def test_verify_wrong_code(self):
        """Test verification with wrong code"""

        self.otp_service.create_otp()

        is_valid, message = self.otp_service.verify_code('000000')

        self.assertFalse(is_valid)
        self.assertIn('invalid', message.lower())


    def test_expiredt_code(self):
        """Test verification with expired code"""

        OTP_Code.objects.update_or_create(
            phone_number=self.phone_number,
            defaults={
                'code': 123456, 
                'created_at': timezone.now() - timedelta(minutes=8)
            }
        )

        is_valid, message = self.otp_service.verify_code('123456')
        
        self.assertFalse(is_valid)
        self.assertIn('expired', message.lower())


    def test_no_otp(self):
        """Test verification with a code that dosnt exist"""
        is_valid, message = self.otp_service.verify_code('123456')

        self.assertFalse(is_valid)
        self.assertIn('cannot find', message.lower())


    def test_empty_code(self):
        """Test verification with an empty code"""

        self.otp_service.create_otp()

        is_valid, message = self.otp_service.verify_code('')

        self.assertFalse(is_valid)
        self.assertIn('required', message.lower())


    def test_non_numeric_code(self):
        """Test verification with an none numeric code"""
        
        self.otp_service.create_otp()
        is_valid, message = self.otp_service.verify_code('abcn45')

        self.assertFalse(is_valid)
        self.assertIn('format', message.lower())
    


#=====OTP deleting tests================================

    def test_otp_deleted_after_success(self):

        code = self.otp_service.create_otp()
        self.otp_service.verify_code(str(code))

        otp_exist = OTP_Code.objects.filter(phone_number=self.phone_number).exists()

        self.assertFalse(otp_exist)

    def test_otp_not_deleted_after_failed_verifaication(self):

        self.otp_service.create_otp()
        self.otp_service.verify_code('000000')
        
        otp_exist = OTP_Code.objects.filter(phone_number=self.phone_number).exists()
        self.assertTrue(otp_exist)

    
    def test_expirde_otp_deleted_on_check(self):
        OTP_Code.objects.update_or_create(
            phone_number=self.phone_number,
            defaults={
                'code':123456,
                'created_at': timezone.now() - timedelta(minutes=8)
            }
        )

        self.otp_service.verify_code('123456')

        otp_exist = OTP_Code.objects.filter(phone_number=self.phone_number).exists()

        self.assertFalse(otp_exist)        


#====== Handle response error test===================================

    def test_handle_error_expired(self):
        response_data, should_clear = OTP_Service.handle_verification_errors(
            'the one time password is expired.'
        )


        self.assertTrue(should_clear)
        self.assertTrue(response_data['redirect'])
        self.assertFalse(response_data['can_retry'])        


    def test_handle_error_not_found(self):
        response_data, should_clear = self.otp_service.handle_verification_errors(
            'cannot find the one time password for this number.'
        )

        self.assertTrue(should_clear)
        self.assertTrue(response_data['redirect'])


    def test_handle_error_invalid_code(self):
        response_data, should_clear = self.otp_service.handle_verification_errors(
            'Invalid code. try again'
        )

        self.assertFalse(should_clear)
        self.assertFalse(response_data['redirect'])
        self.assertTrue(response_data['can_retry'])



#=====Edge cases====================================================

    def test_multiple_otp_for_same_phone(self):
        """Test that creating multiple OTP's works correctly"""

        code1 = self.otp_service.create_otp()
        code2 = self.otp_service.create_otp()

        is_valid1, _ = self.otp_service.verify_code(code1)
        is_valid2,_ = self.otp_service.verify_code(code2)

        self.assertFalse(is_valid1)
        self.assertTrue(is_valid2)

    
    def test_different_phone_have_different_code(self):
        """Test OTP's for different phones are independent"""
        code1 = self.otp_service.create_otp()
        
        otp_service2 = OTP_Service('09222222222')
        code2 = otp_service2.create_otp()

        is_valid1, _ = self.otp_service.verify_code(code1)
        is_valid2, _ = otp_service2.verify_code(code2)

        self.assertTrue(is_valid1)
        self.assertTrue(is_valid2)