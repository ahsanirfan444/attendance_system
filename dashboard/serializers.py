from django.contrib.auth.models import User
from rest_framework import serializers
from datetime import datetime
from attendance_api.models import attendance, client
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from dashboard.models import Shift


class CreateShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = '__all__'

    def create(self, validated_data):
        shift_obj = Shift.objects.create(**validated_data,is_active=True)
        return shift_obj
    
    def validate(self, value):
        shift_name = value['name']
        name = Shift.objects.filter(name=shift_name).exists()
        if name:
            raise serializers.ValidationError("Already exist with this name")
        shift_name.replace(' ','_').replace('-','_')
        return value



class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','first_name','last_name',)
        
class ShiftListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shift
        fields = ('id','name','start_time','end_time','grace_min','halfday_limit','absent_time_limit','early_out_time')