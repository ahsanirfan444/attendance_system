from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.serializers import VerifyJSONWebTokenSerializer
from rest_framework_jwt.views import ObtainJSONWebToken
from user_management.serializers import AppUserSerializer, SendOtpSerializer, VerifyOtpSerializer, \
    ChangePasswordSerializer


class CustomAuthLogin(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        valid_data = VerifyJSONWebTokenSerializer().validate(response.data)
        user = valid_data['user']
        response.data['username'] = user.username
        response.data['first_name'] = user.first_name
        response.data['last_name'] = user.last_name
        response.data['user_id'] = user.id

        return Response(
                        {'error': '', 'error_code': '', 'data': response.data}, status=200)

class AppUser(APIView):

    def post(self, request, *args, **kwargs):
        try:

            user_serializer = AppUserSerializer(context={'request': request}, data=request.data)
            if user_serializer.is_valid():
                user_serializer.save()
                return Response(
                    {'error': '', 'error_code': '', 'data': user_serializer.initial_data}, status=200)
            else:
                return Response({'error': user_serializer.errors, 'error_code': 'HS002', 'data':''}, status=200)
        
        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': ''}, status=400)


class SendOtp(APIView):

    def post(self, request, *args, **kwargs):
        try:
            otp_serializer = SendOtpSerializer(data=request.data)
            if otp_serializer.is_valid():
                otp_serializer.save()
                return Response(
                    {'error': '', 'error_code': '', 'message': 'OTP code has been sent'}, status=200)
            else:
                error = otp_serializer.errors.keys()
                return Response({'error': error, 'error_code': 'HS002', 'message': ''}, status=200)
        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': ''}, status=400)


class VerifyOtp(APIView):

    def post(self, request, *args, **kwargs):
        try:
            verify_otp_serializer = VerifyOtpSerializer(data=request.data)
            if verify_otp_serializer.is_valid():
                verify_otp_serializer.save()
                if verify_otp_serializer.instance['status'] == 'verified':
                    return Response({'error': '', 'error_code': '', 'message': 'verified'}, status=200)
                else:
                    return Response({'error': 'Invalid OTP', 'error_code': '', 'message': ''},
                                    status=200)
            else:
                error = ', '.join(
                    ['{0}:{1}'.format(k, str(v[0])) for k, v in verify_otp_serializer.errors.items()])
                return Response({'error': error, 'error_code': 'HS002', 'data': {}}, status=200)
        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': {}}, status=400)


class ChangePassword(APIView):

    def post(self, request, *args, **kwargs):
        try:
            change_pass_serializer = ChangePasswordSerializer(data=request.data)
            if change_pass_serializer.is_valid():
                change_pass_serializer.save()
                return Response(
                    {'error': '', 'error_code': '', 'change_password_data': change_pass_serializer.data}, status=200)
            else:
                return Response({'error': change_pass_serializer.errors.keys(), 'error_code': 'HS002', 'change_password_data': ''}, status=200)

        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': ''}, status=400)