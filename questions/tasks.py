from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from custom_user.tokens import email_confirm_token
from questions.models import Book, Docs

User = get_user_model()


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def send_book_email(self, book_id, email):
    """
    Sends book email with attachments.
    Runs asynchronously via Celery.
    """

    try:
        book = Book.objects.get(id=book_id)

        subject = f"Your Kenlib Order: {book.title}"
        html_message = render_to_string(
            "questions/booksale.html",
            {"book": book}
        )

        message = EmailMessage(
            subject=subject,
            body=html_message,
            from_email="Kenlib@ken-lib.com",
            to=[email],
        )
        message.content_subtype = "html"

        docs = Docs.objects.filter(book=book)

        for doc in docs:
            if doc.file and doc.file.path:
                message.attach_file(doc.file.path)

        message.send(fail_silently=False)

    except Book.DoesNotExist:
        # optionally log
        pass

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def send_registration_confirmation_email(self, user_id):
    """
    Email a signed confirmation link after registration (uid + token pattern).
    """
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return

    if user.email_verified:
        return

    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_confirm_token.make_token(user)
    base = getattr(settings, 'EMAIL_CONFIRMATION_API_BASE_URL', '').rstrip('/')
    confirm_url = f"{base}/api/confirm-email/{uid}/{token}/"

    subject = 'Confirm your email address'
    html_message = render_to_string(
        'questions/registration_confirm_email.html',
        {
            'first_name': user.first_name,
            'confirm_url': confirm_url,
        },
    )

    message = EmailMessage(
        subject=subject,
        body=html_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )
    message.content_subtype = 'html'
    message.send(fail_silently=False)


@shared_task
def send_test_email():
    send_mail(
        'Using SparkPost with Django123',
        'This is a message from Django using SparkPost!123',
        'Kenlib@ken-lib.com',
        ['bestessays001@gmail.com'],
        fail_silently=False
    )