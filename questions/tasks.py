from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_welcome_email(user_id, email, username):
    send_mail(
        subject='Welcome to Our Platform!',
        message=f'Hi {username}, thanks for joining!',
        from_email='no-reply@yourdomain.com',
        recipient_list=[email],
        fail_silently=False,
    )


@shared_task
def send_test_email():
    send_mail(
        'Using SparkPost with Django123',
        'This is a message from Django using SparkPost!123',
        'Kenlib@ken-lib.com',
        ['bestessays001@gmail.com'],
        fail_silently=False
    )