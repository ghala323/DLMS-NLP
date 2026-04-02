from rest_framework import serializers

from django.contrib.auth import get_user_model

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Profile


User = get_user_model()


class NationalIDTokenSerializer(TokenObtainPairSerializer):

    username_field = 'national_id'


class RegisterSerializer(serializers.ModelSerializer):

    national_id = serializers.CharField()

    phone_number = serializers.CharField()

    confirm_password = serializers.CharField(write_only=True)

    class Meta:

        model = User

        fields = (

            'first_name',
            'last_name',
            'email',
            'national_id',
            'password',
            'confirm_password',
            'phone_number'

        )

        extra_kwargs = {

            'password': {'write_only': True}

        }

    def validate(self,data):

        if data['password'] != data['confirm_password']:

            raise serializers.ValidationError(
                "Passwords do not match"
            )

        return data


    def create(self,validated_data):

        phone_number = validated_data.pop('phone_number')

        validated_data.pop('confirm_password')

        validated_data['username'] = validated_data['national_id']

        user = User.objects.create_user(**validated_data)

        Profile.objects.create(

            user=user,
            phone_number=phone_number

        )

        return user


class UserSerializer(serializers.ModelSerializer):

    class Meta:

        model = User

        fields = [
            'id',
            'national_id',
            'email',
            'first_name',
            'last_name'
        ]