from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.views import APIView
from . import serializer 
from utils.otp_service import OTP_Service
from utils.session_helpers import OTPSessionCleanUp
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
import time

User = get_user_model()



class UserRegister(APIView):

    permission_classes = [permissions.AllowAny]


    def post(self, request):

        serialized_data = serializer.UserRegisterSerializer(data=request.data)

        if serialized_data.is_valid():
            phone_number=serialized_data.validated_data['phone_number']
            otp = OTP_Service(phone_number)
            otp.create_otp()

            OTPSessionCleanUp.clear_session(request)

            request.session['user_register_session'] = {
                'username': serialized_data.validated_data['username'],
                'phone_number':serialized_data.validated_data['phone_number'],
                'email':serialized_data.validated_data['email'],
                'password':serialized_data.validated_data['password']
            }
            request.session['otp_send_count'] = 0

            return Response({'detail':"one time password sent to phone number",
                             'phone number': phone_number[-4:]}, status=status.HTTP_200_OK)
        
        return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyUserPhone(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):

        user_session = request.session.get('user_register_session')
        if not user_session:
             return Response({
                'detail': 'Session expired. Please register again.',
                'redirect': reverse('accounts:user_register')
            }, status=400)
        
        user_phone = user_session['phone_number']

        
        serialized_data = serializer.UserConfirmOTPCode(data=request.data)

        if not serialized_data.is_valid():
            return Response({'error':serialized_data.errors}, status=400)
        
        otp_service = OTP_Service(phone_number=user_phone)
        is_valid, message = otp_service.verify_code(serialized_data.validated_data['code'])

        if not is_valid:

            response_data, should_clear = OTP_Service.handle_verification_errors(message)
            
            if should_clear:
                request.session.pop('user_register_session', None)
                request.session.pop('otp_send_count', None)
            return Response(response_data, status=400)
            

        user = User.objects.create_user(
            phone_number = user_phone,
            username = user_session['username'],
            email = user_session.get('email'),
            password = user_session['password']
        )
        request.session.pop('user_register_session', None)
        request.session.pop('otp_send_count', None)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'detail': 'Registration successful!',
            'token': token.key,
            'user': {
                'phone_number': user.phone_number,
                'username': user.username,}
        }, status=201)
    

class UserLoginWithPassword(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serialized_data = serializer.UserLoginWithPasswordSerializer(data=request.data)

        if not serialized_data.is_valid():

            return Response(serialized_data.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        
        identifier = serialized_data.validated_data['identifier']
        password = serialized_data.validated_data['password']

        user = authenticate(request, identifier=identifier, password=password)
        if not user:
            return Response({'detail':'Invalid user name or password'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
        if not user.is_active:
            return Response({'detail':'Account is deactivated.'},
                             status=status.HTTP_403_FORBIDDEN)

        token, _ = Token.objects.get_or_create(user=user)
        return Response({'token':token.key}, status=status.HTTP_200_OK)

           




class UserLoginWithOTP(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
       
        serialized_data = serializer.UserLoginSendOTPSerializer(data=request.data)
        if not serialized_data.is_valid():

            return Response(serialized_data.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user_phone = serialized_data.validated_data['phone_number']
        
        OTPSessionCleanUp.clear_session(request)

        if User.objects.filter(phone_number=user_phone).exists():
            request.session['login_phone'] = user_phone
            request.session['otp_send_count'] = 0
            otp_service = OTP_Service(user_phone)
            otp_service.create_otp()
        

        else:
            time.sleep(0.5)

        return Response({'detail':"If this phone number is registered, you will receive an OTP."},
                            status=status.HTTP_200_OK)


            
class UserLoginVerifyOTP(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):

        user_phone = request.session.get('login_phone')
        if not user_phone:
            return Response({'detail':'sessions are expired or missed. request for another otp'},
                            status=status.HTTP_400_BAD_REQUEST)
        

        serialized_data = serializer.UserConfirmOTPCode(data=request.data)
        if not serialized_data.is_valid():
            return Response({'error':serialized_data.errors},
                             status=status.HTTP_400_BAD_REQUEST)
        
        otp_service = OTP_Service(user_phone)
        is_valid , message = otp_service.verify_code(serialized_data.validated_data['code'])

        if not is_valid:
                response_data, should_clear = OTP_Service.handle_verification_errors(message)
                
                if should_clear:
                    request.session.pop('login_phone', None)
           
                
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


        user = User.objects.get(phone_number=user_phone)

        if not user.is_active:
            request.session.pop('login_phone', None)
            return Response({
                'detail':"user is deactivated"
            }, status=status.HTTP_403_FORBIDDEN)
        
        request.session.pop('login_phone', None)

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            'token':token.key,
            'user':{
                'phone_number':user.phone_number,
                'username':user.username
            }
        }, status=status.HTTP_200_OK)




class UserLoggingOut(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        deleted, _ = Token.objects.filter(user=request.user).delete()

        if deleted:
            return Response({'detail':'Logged out successfully.'},
                            status=200)
        
        return Response({
             'detail': 'No active token found.'
            }, status=status.HTTP_404_NOT_FOUND)

        



class ResendOTPView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        phone_number = self._get_phone_from_session(request)

        if not phone_number:
            return Response(
                {'detail': 'No active OTP request found. Please start again.'}
                , status=status.HTTP_400_BAD_REQUEST)


        otp_send_count = request.session.get('otp_send_count', 0)

        if otp_send_count >= 3:
            request.session.pop('otp_send_count', None)
            return Response({'detail':'Too many OTP request. please try again later.'},
                            status=status.HTTP_429_TOO_MANY_REQUESTS)


        otp_service = OTP_Service(phone_number=phone_number)
        otp_service.create_otp()
        request.session['otp_send_count'] = request.session.get('otp_send_count', 0) + 1

        return Response({'detail':"New OTP sent successfully",
                              'phone number':phone_number[-4:],
                              'attempts left': 3 - (otp_send_count + 1)})
        


    def _get_phone_from_session(self, request):

        register_session = request.session.get('user_register_session')
        if register_session:

            return register_session.get('phone_number')
        
        login_phone = request.session.get('login_phone')
        if login_phone:
            return login_phone

        new_phone = request.session.get('new_phone_number')
        if new_phone:
            return new_phone 

        return None



class UserProfileView(APIView):

    permission_classes = [permissions.IsAuthenticated]


    def get(self, request):

        serializer_data = serializer.UserProfileSerializer(instance=request.user)
        return Response(serializer_data.data, status=status.HTTP_200_OK)

        

class UsernameChangeView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def put(self, request):

      

        serialized_data = serializer.UserUpdateUsernameSerializer(
            instance=request.user, data=request.data, partial=True
        )
        if serialized_data.is_valid():
            serialized_data.save()
            return Response({'data':serialized_data.data, 'detail':"username successfully updated."},
                            status=200)
        
        return Response(serialized_data.errors, status=400)
    



class RequestChangingPhoneNumber(APIView):

    permission_classes = [permissions.IsAuthenticated]


    def post(self, request):

        serialized_data = serializer.UserUpdatePhoneNumber(data=request.data)
        if not serialized_data.is_valid():
            return Response(serialized_data.errors, status=400)
        
        new_phone = serialized_data.validated_data['new_phone_number']
        
        OTPSessionCleanUp.clear_session(request)

        request.session['new_phone_number'] = new_phone
        request.session['otp_send_count'] = 0

        otp_service = OTP_Service(new_phone)
        otp_service.create_otp()

        return Response({
            'detail':"OTP sent to new phone number.",
            'phone_number' : new_phone[-4:]
        },status=200)
    


class ConfirmPhoneUpdateView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        new_phone = request.session.get('new_phone_number')
        if not new_phone:
            return Response({
                'detail': 'Session expired. Please register again.',
                'redirect': reverse('accounts:changing_number')
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializede_data = serializer.UserConfirmOTPCode(data=request.data)
        if not serializede_data.is_valid():
            return Response(serializede_data.errors, status=400)
        

        otp_service = OTP_Service(new_phone)
        is_valid, message = otp_service.verify_code(serializede_data.validated_data['code'])

        if not is_valid:

            response_data, should_clear_session = OTP_Service.handle_verification_errors(message)
            if should_clear_session:
                request.session.pop('new_phone_number', None)
                request.session.pop('otp_send_count', None)
            
            return Response(response_data, status=400)
            
        user = request.user
        user.phone_number = new_phone
        user.save(update_fields=['phone_number', 'updated_at'])

        request.session.pop('new_phone_number', None)
        request.session.pop('otp_send_count', None) 

     

        return Response({
            'detail': 'Phone number updated successfully.',
            
        })



class CancelPhoneChangeView(APIView):

    permission_classes = [permissions.IsAuthenticated]


    def post(self, request):

        request.session.pop('new_phone_number', None)
        request.session.pop('otp_send_count', None)

        return Response({
            'detail':"phone number change cancelled."
        })




