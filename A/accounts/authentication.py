from django.contrib.auth.backends import BaseBackend
from django.db.models import Q
from .models import User



class IdentifierAuthentication(BaseBackend):

    """
    a custom authentication for users to be able to login with either username
    or phone number
    """

    def authenticate(self, request, identifier=None, password=None):
        if not identifier or not password:
            return None
        
        user = User.objects.filter(
            Q(username=identifier) | Q(phone_number=identifier)
        ).first()

        if user and user.check_password(password) :
            return user
        
        return None



    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        
        except User.DoesNotExist:
            return None

