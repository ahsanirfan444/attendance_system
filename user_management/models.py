from django.db import models
from django.contrib.auth.models import User


class OtpToken(models.Model):
    i_user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    mob_otp_code = models.CharField(max_length=6)
    email_otp_code = models.CharField(max_length=6)
    creation_time = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'otp_token'


    