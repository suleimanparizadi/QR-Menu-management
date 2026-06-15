from accounts.models import OTP_Code
import random
from django.utils import timezone




class OTP_Service:

    """
    A service to handling one time password, generate and verify it.
    """


    def __init__(self, phone_number):
        self.phone_number = phone_number

    
    def generate_code(self):
        """
        generate a 6 digit code.
        """
        return random.randint(111111, 999999)
    

    def send_otp(self, code):
        """
        send otp via SMS
        Integrate with the SMS provider here.
        """
        # just for developer:
        print(f"the OTP for {self.phone_number} is {code}")

        # return True or False based on SMS sending success

        return True
    

        
    def create_otp(self):
        code = self.generate_code()

        OTP_Code.objects.update_or_create(
            phone_number = self.phone_number,
            defaults= {'code': code, 'created_at':timezone.now()}
        )

        self.send_otp(code)
        print(code)

        return code
    
    def verify_code(self, input_code):
        """
        verifying the input otp code by user 
        """

        if not input_code:
            return False, "code is required."
        
        try:
            otp = OTP_Code.objects.get(phone_number= self.phone_number)
        except OTP_Code.DoesNotExist:
            return False, "cannot find the one time password for this number."
        
        if otp.is_expired():
            otp.delete()
            return False, "the one time password is expired."


        # validate the OTP format

        try:
            input_code = int(input_code)

        except (ValueError, TypeError):
            return False, "Invalid code format"

        if otp.code != input_code:
            return False, "Invalid code. try again"
        
        otp.delete()
        return True, "one time password verifier successfully."
    
    @staticmethod
    def handle_verification_errors(message):

        should_clear_session = (
            "expired" in message.lower() or
            "cannot find" in message.lower()
        )

        response_data = {
            'detail':message,
            'redirect':  should_clear_session,
            'can_retry': not should_clear_session
            }
        
        return response_data, should_clear_session

        

