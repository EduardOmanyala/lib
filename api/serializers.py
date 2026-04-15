from rest_framework import serializers
from custom_user.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'profile_pic', 'email_verified')
        read_only_fields = ('id', 'email_verified')

class RegisterSerializer(serializers.ModelSerializer):
    pass1 = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    pass2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'pass1', 'pass2', 'first_name')

    def validate_first_name(self, value):
        value = (value or '').strip()
        if not value:
            raise serializers.ValidationError('This field may not be blank.')
        return value

    def validate(self, attrs):
        if attrs['pass1'] != attrs['pass2']:
            raise serializers.ValidationError({'pass1': 'Password fields did not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('pass2')
        password = validated_data.pop('pass1')
        email = validated_data.pop('email')
        user = User.objects.create_user(email, password, **validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid email or password.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
        else:
            raise serializers.ValidationError('Must include "email" and "password".')

        attrs['user'] = user
        return attrs

