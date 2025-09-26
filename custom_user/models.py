import random
from django.db import models
from django.templatetags.static import static
from django_use_email_as_username.models import BaseUser, BaseUserManager


PROFILE_PIC_CHOICES = [
    'analytics/imgs/person.png',
    'analytics/imgs/person2.jpg',
    'analytics/imgs/person3.jpg',
    'analytics/imgs/person4.jpg',
    'analytics/imgs/person5.jpg',
    'analytics/imgs/person6.jpg',
    'analytics/imgs/person7.jpg',
]




class User(BaseUser):
    profile_pic = models.CharField(max_length=100, blank=True, null=True)
    objects = BaseUserManager()


    def save(self, *args, **kwargs):
        if not self.profile_pic:
            self.profile_pic = random.choice(PROFILE_PIC_CHOICES)
        super().save(*args, **kwargs)

    @property
    def img(self):
        return static(self.profile_pic)

#<img src="{{ user.img }}" alt="Profile Picture">