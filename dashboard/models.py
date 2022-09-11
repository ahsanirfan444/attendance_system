from django.db import models
from django.contrib.auth.models import User

DAYS = (('mon', 'Monday'), ('tue', 'Tuesday'),('wed', 'Wednesday'),('thu', 'Thursday'),('fri', 'Friday'),('sat', 'Saturday'),('sun', 'Sunday'))

class Shift(models.Model):
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    grace_min = models.PositiveIntegerField()
    halfday_limit = models.PositiveIntegerField()
    absent_time_limit = models.PositiveIntegerField()
    early_out_time = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    class Meta:
        db_table = 'shift'
        
class Profile(models.Model):
    i_user = models.OneToOneField(User, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift,on_delete=models.DO_NOTHING)
    department = models.CharField(max_length=100)
    class Meta:
        db_table = 'profile'

        
class WorkingDay(models.Model):
    i_shift = models.ForeignKey(Shift,on_delete=models.DO_NOTHING)
    day = models.CharField(max_length =3,choices = DAYS)
    class Meta:
        db_table = 'working_day'