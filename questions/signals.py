from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Purchases, MyNotifications


@receiver(post_save, sender=Purchases)
def create_notification_on_purchase(sender, instance, created, **kwargs):
    if created:
        MyNotifications.objects.create(
            user=instance.user,
            book=instance.book,
            text=f"You purchase is ready {instance.book.title}"
        )