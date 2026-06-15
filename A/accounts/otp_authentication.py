from django.contrib.auth.backends import BaseBackend
from utils.otp_service import OTP_Service
from django.contrib.auth import get_user_model

User = get_user_model()

class OTPAuthentication(BaseBackend):

    """
    Authentication by OTP password 
    using the OPT_Service in utils.py 
    """

    def authenticate(self, request, phone_number=None, otp_code=None):
        if not phone_number or not otp_code:
            return None
        
        otp_service = OTP_Service(phone_number)
        is_valid, message = otp_service.verify_code(otp_code)

        if not is_valid:
            return None
        
        try:
            user = User.objects.get(phone_number=phone_number, is_active=True)
            return user
        except User.DoesNotExist:
            return None
        
    
    # user login return user and Django store the user id in sessions
    # for any request after authentication Django calls get_user(user_id) 
    # without it authentication only work for just one request

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        
        except User.DoesNotExist:
            return None