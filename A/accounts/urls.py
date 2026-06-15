from django.urls import path
from . import views

app_name = 'accounts'


urlpatterns = [

    # Registration
    path('register/', views.UserRegister.as_view(), name='user_register'),
    path('verify/', views.VerifyUserPhone.as_view(), name='verify_register'),

    # Login with password and identifier
    path('login/password/', views.UserLoginWithPassword.as_view(), name='login_password'),
    
    # Login with one time password
    path('login/otp/send/', views.UserLoginWithOTP.as_view(), name='login_otp_send'),
    path('login/otp/verify/', views.UserLoginVerifyOTP.as_view(), name='login_otp_verify'),

    # Resend OTP
    path('otp/resend/', views.ResendOTPView.as_view(), name='otp_resend'),


    # Logout
    path('logout/', views.UserLoggingOut.as_view(), name='logout'),

    #profile
    path('profile/', views.UserProfileView.as_view(), name='profile_view'),

    #Profile update
    path('profile/username/', views.UsernameChangeView.as_view(), name='change_username'),
    path('profile/change_number/', views.RequestChangingPhoneNumber.as_view(), name='changing_number'),
    path('profile/change_number/confirm/', views.ConfirmPhoneUpdateView.as_view(), name='phone_change_confirm'),
    path('profile/change_number/cancel/',views.CancelPhoneChangeView.as_view(),name='cancel_phone_change'),

]

