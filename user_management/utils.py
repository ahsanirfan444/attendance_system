import random
from rest_framework.views import exception_handler
from rest_framework.response import Response
gender_dict = {'M': 'Male', 'F': 'Female'}

def generate_otp_tokens():
    code_dict = dict()
    code_dict['email_code'] = ''.join(str(random.randint(1, 9)) for _ in range(0, 6))
    code_dict['sms_code'] = ''.join(str(random.randint(1, 9)) for _ in range(0, 6))
    return code_dict



def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    # for login error
    if response is None:
        return Response(
            {'error': 'Invalid Credentials', 'error_code': 'HI005', 'message': '', 'data': {}},
            status=200)
    if response is not None:
        response.data['status_code'] = response.status_code
    return Response(
        {'error': ['The signature is not verified'], 'error_code': 'HI005', 'message': '', 'data': {}},
        status=401)