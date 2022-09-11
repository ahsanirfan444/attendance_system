from django.db import models

_PORT_CHOICES = (('SSL', 'TLS/SSL'), ('StartTLS', 'STARTTLS'), ('None', 'None'))
TYPE_CHOICES = (('587', '587'), ('465', '465'), ('25', '25'))


class EmailConfiguration(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=128)
    host = models.CharField(max_length=128)
    port = models.CharField(max_length=8, default='465', choices=TYPE_CHOICES, verbose_name = "Port *")
    port_type = models.CharField(max_length=8, default='TLS/SSL',
                                 choices=_PORT_CHOICES, verbose_name = "Port Type *")

    class Meta:
        db_table = 'email_configuration'
