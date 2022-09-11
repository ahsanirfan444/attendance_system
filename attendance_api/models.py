from django.db import models
from django.contrib.auth.models import User

class client(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    longitude = models.CharField(max_length=200)
    latitude = models.CharField(max_length=200)
    radius = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'client'

class attendance(models.Model):
    i_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    punch_in_latitude = models.CharField(max_length=100,null=True,blank=True)
    punch_in_longitude = models.CharField(max_length=100,null=True,blank=True)
    punch_out_latitude = models.CharField(max_length=100,null=True,blank=True)
    punch_out_longitude = models.CharField(max_length=100,null=True,blank=True)
    punch_in_image_path = models.CharField(max_length=200,null=True,blank=True)
    punch_out_image_path = models.CharField(max_length=200,null=True,blank=True)
    punch_in_note = models.CharField(max_length=200,null=True,blank=True)
    punch_out_note = models.CharField(max_length=200,null=True,blank=True)
    punch_in_time = models.DateTimeField(null=True,blank=True)
    punch_out_time = models.DateTimeField(null=True,blank=True)
    user_punch_in_status = models.CharField(max_length=50,null=True,blank=True)
    user_punch_out_status = models.CharField(max_length=50,null=True,blank=True)
    i_client = models.ForeignKey(client, on_delete=models.DO_NOTHING,null=True,blank=True)
    class Meta:
        db_table = 'attendance'


