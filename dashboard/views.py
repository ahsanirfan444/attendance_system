from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from dashboard.models import Shift

from dashboard.serializers import CreateShiftSerializer, ShiftListSerializer, UserListSerializer

class CreateShiftAPI(APIView):
    def post(self, request, *args, **kwargs):
        # permission_classes = (IsAuthenticated,)
        serializer = CreateShiftSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'error': '', 'error_code': '', 'data':serializer.data}, status=200)
        else:
            return Response({'error': serializer.errors, 'error_code': 'H402', 'data':{}}, status=200)
        
        
class UsersListAPI(APIView):
    def get(self, request):
        try:
            user_obj = User.objects.filter(is_active=True).order_by('-id')
            data = UserListSerializer(user_obj,many=True)
            if data:
                return Response(
                    {'error': '', 'error_code': '', 'data': data.data}, status=200)
            else:
                return Response({'error': data.errors, 'error_code': 'HS002', 'data': ''}, status=200)
        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': ''}, status=400)
        
class ShiftListAPI(APIView):
    def get(self, request):
        try:
            shift_obj = Shift.objects.filter(is_active=True).order_by('-id')
            data = ShiftListSerializer(shift_obj,many=True)
            if data:
                return Response(
                    {'error': '', 'error_code': '', 'data': data.data}, status=200)
            else:
                return Response({'error': data.errors, 'error_code': 'HS002', 'data': ''}, status=200)
        except Exception as error:
            return Response({'error': repr(error), 'error_code': 'H007', 'matched': 'N', 'data': ''}, status=400)
