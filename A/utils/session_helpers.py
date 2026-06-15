


class OTPSessionCleanUp:



    @staticmethod
    def clear_session(request):

        key_session = [
            'user_register_session',
            'login_phone',
            'new_phone_number',
            'otp_send_count',
        ]

        for key in key_session:
            request.session.pop(key, None)