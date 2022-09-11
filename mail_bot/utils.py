from django.core.mail import get_connection
from django.core.mail import send_mail


def send_email_func(send_email_obj, subject, users_list=[], attachment=None, body_text=None, html_message=None):
    response = 0
    email = send_email_obj.email
    password = send_email_obj.password
    email_host = send_email_obj.host
    port = int(send_email_obj.port)
    connection = get_connection(host=email_host,
                                port=port,
                                username=email,
                                password=password,
                                use_tls=True)

    response = send_mail(subject, body_text, email, users_list, connection=connection, html_message=html_message)
    return response