from django.contrib.auth.models import User
from rest_framework import serializers
from datetime import datetime, timedelta
from dashboard.models import Profile, Shift
from mail_bot.models import EmailConfiguration
from mail_bot.utils import send_email_func
from user_management.models import OtpToken
from user_management.utils import generate_otp_tokens


class AppUserSerializer(serializers.ModelSerializer):
    department = serializers.CharField(max_length=15)
    shift = serializers.IntegerField()

    class Meta:
        model = User
        exclude = ('username','is_staff', 'date_joined', 'user_permissions', 'groups', 'last_login', 'is_superuser')
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data['username'] = validated_data['email']
        shift = validated_data['shift']
        department= validated_data['department']
        del validated_data['shift']
        del validated_data['department']
        shift_obj = Shift.objects.filter(id=shift)[0]
        validated_data['is_active'] = False
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(i_user=user,department=department,shift=shift_obj)

        code_dict = generate_otp_tokens()
        OtpToken.objects.create(i_user=user, mob_otp_code=code_dict['sms_code'], email_otp_code=code_dict['email_code'])
        email_config_obj = EmailConfiguration.objects.get()
        html_message = "Your otp verification code is %s " % code_dict['email_code']
        # send_email_func(email_config_obj, 'OTP verification code', [validated_data['email']], html_message=html_message)
        return user

    def validate_email(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('Email already taken')
        return value
    
    def validate_shift(self, value):
        if not Shift.objects.filter(id=value).exists():
            raise serializers.ValidationError('Not valid shift')
        return value

class SendOtpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=13)

    def create(self, validated_data):
        # test
        OtpToken.objects.filter(i_user__username=validated_data['email']).delete()
        code_dict = generate_otp_tokens()
        user = User.objects.get(username=validated_data['email'])
        otp_obj = OtpToken.objects.create(i_user=user, mob_otp_code=code_dict['sms_code'],
                                          email_otp_code=code_dict['email_code'])

        email_config_obj = EmailConfiguration.objects.get()
        html_message = "Your otp verification code is %s " % code_dict['email_code']
        send_email_func(email_config_obj, 'OTP verification code', [otp_obj.i_user.email], html_message=html_message)
        return otp_obj

    def validate_username(self, value):
        if not (User.objects.filter(username=value).exists()):
            raise serializers.ValidationError('no data found')
        return value


class VerifyOtpSerializer(serializers.Serializer):
    # mob_otp_code = serializers.CharField(max_length=6)
    email_otp_code = serializers.CharField(max_length=6)
    email = serializers.EmailField()

    def create(self, validated_data):
        if OtpToken.objects.filter(email_otp_code=validated_data['email_otp_code']).exists():
            # otp_obj = OtpToken.objects.get(email_otp_code=validated_data['email_otp_code'],
            user_id = (User.objects.get(username = validated_data['email'])).id         
            otp_obj = OtpToken.objects.get(email_otp_code=validated_data['email_otp_code'],i_user_id=user_id)
            cr_time = otp_obj.creation_time.replace(tzinfo=None)
            t2 = cr_time + timedelta(minutes=5)
            if datetime.now() > t2:
                return {'status': 'Failed to verify'}
            else:
                otp_obj.delete()
                user_obj = User.objects.get(id=user_id)
                user_obj.is_active = True
                user_obj.save()
        else:
            return {'status': 'Failed to verify'}
        return {'status': 'verified'}

    def validate_email_otp(self, value):
        if len(value) > 6 or len(value) < 6:
            raise serializers.ValidationError('please enter 6 digit number')
        return value


class ChangePasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.get(username=validated_data['email'])
        print(user, 'user')
        user.set_password(validated_data['password'])
        user.save()
        return user

    def validate_username(self, value):
        if not (User.objects.filter(username=value).exists()):
            raise serializers.ValidationError('no data found')
        return value



