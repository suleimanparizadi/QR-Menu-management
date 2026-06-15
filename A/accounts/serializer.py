from rest_framework import serializers
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class UserRegisterSerializer(serializers.ModelSerializer):


    password = serializers.CharField(
        write_only = True,
        min_length = 4,
        style = {'input_type':'password'}
    )

    password_confirm = serializers.CharField(
        write_only = True,
        style = {'input_type':'password'}
    )    

    class Meta:
        model = User
        fields = ['phone_number', 'username', 'email', 'password', 'password_confirm']


    def validate(self, data):

        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({
                'password_confirm':"passwords must be match."
            })

        return data
        
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data, password=password)
        return user
    

class UserLoginWithPasswordSerializer(serializers.Serializer):
    """
    For login with password and identifier(username/phone number)
    """

    identifier = serializers.CharField()
    password = serializers.CharField(style = {'input_type':'password'})


class UserLoginSendOTPSerializer(serializers.Serializer):
    """
    When users ask an one time password to login
    validate phone number before create and send the one time password
    """
    phone_number = serializers.CharField(required = True, max_length = 11)

    def validate_phone_number(self, value):
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError("wrong format for phone number")

        return value

class UserConfirmOTPCode(serializers.Serializer):
    """
    for when users confirm the one time password and enter the code for login
    only validate the on time password format
    """

    code = serializers.CharField(required = True)

    def validate_code(self, value):
        if not value:
            raise serializers.ValidationError("The code is requeired")

        return value


class UserProfileSerializer(serializers.ModelSerializer):
    
    """
    View the profile 
    """

    class Meta:
        model = User
        fields = ['username', 'phone_number', 'email', 'created_at']
        read_only_fields = ['phone_number', 'created_at']


class UserUpdateUsernameSerializer(serializers.Serializer):

    """
    Changing username - format validation only
    """

    username = serializers.CharField(required=True, max_length = 125)

    def validate_username(self, value):
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)

        if queryset.exists():
            raise serializers.ValidationError("This username is already taken.")

        return value
    
    def update(self, instance, validated_data):
        instance.username = validated_data['username']
        instance.save(update_fields = ['username', 'updated_at'])

        return instance
    

class UserUpdatePhoneNumber(serializers.Serializer):
    """
    changing user's phone number
    """

    new_phone_number = serializers.CharField(
        required=True, max_length=11)

    def validate_new_phone_number(self, value):
        if User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("This phone number is already registered")
        if not re.match(r'^09\d{9}$', value):
            raise serializers.ValidationError("wrong format for phone number")
        
        return value

