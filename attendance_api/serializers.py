import os
from rest_framework import serializers
from datetime import datetime
from attendance_api.models import attendance, client
from django.conf import settings
from django.core.files.storage import FileSystemStorage


class PunchSerializer(serializers.Serializer):
    image = serializers.ImageField(allow_null=True,required=False)
    longitude = serializers.CharField(allow_null=True) 
    latitude = serializers.CharField(allow_null=True)
    note = serializers.CharField(allow_null=True)
    client_id = serializers.IntegerField(allow_null=True,required=False)
    is_punch_in = serializers.BooleanField()
    image_path = serializers.CharField(required=False)


    def create(self, validated_data):
        user_id = self.context['user_id']
        validated_data['user_id'] = user_id
        
        if 'image' in validated_data:
            if validated_data['is_punch_in']:
                file_full_path = os.path.join(settings.MEDIA_ROOT, 'punched_in_images')
            else:
                file_full_path = os.path.join(settings.MEDIA_ROOT, 'punched_out_images')
                
            file_path = file_full_path.split('media')
            image_path = 'media/'+str(user_id)+file_path[1]
            os.makedirs(image_path, exist_ok=True)
            fs = FileSystemStorage(image_path)
            punch_in_image = validated_data['image']
            if punch_in_image is not None:
                file_name = fs.save(validated_data['image'].name,validated_data['image'])
                image_url = image_path+'/' + file_name
                validated_data['image_path'] = image_url
                del validated_data['image']
            else:
                del validated_data['image']
                validated_data['image_path'] = ''
        else:
            validated_data['image_path'] = ''
        return validated_data
        



class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = client
        fields = '__all__'

    def create(self, validated_data):
        validated_data['is_active'] = True
        client_obj = client.objects.create(**validated_data)

        return client_obj

    def validate_name(self, value):
        if client.objects.filter(name=value).exists():
            raise serializers.ValidationError('This client is already exist')
        value = value.replace('-', '')
        return value
    
    
class AttendanceRecordSerializer(serializers.Serializer):
    start_date = serializers.DateField(allow_null=True,required=False)
    end_date = serializers.DateField(allow_null=True,required=False)
    
    def create(self, validated_data):
        return validated_data