from celery import shared_task
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from questions.models import Book, Docs


@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=30, retry_kwargs={"max_retries": 5})
def send_book_email(self, book_id, email):
    """
    Sends book email with attachments.
    Runs asynchronously via Celery.
    """

    try:
        book = Book.objects.get(id=book_id)

        subject = f"Your Book: {book.title}"
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

@shared_task
def send_test_email():
    send_mail(
        'Using SparkPost with Django123',
        'This is a message from Django using SparkPost!123',
        'Kenlib@ken-lib.com',
        ['bestessays001@gmail.com'],
        fail_silently=False
    )