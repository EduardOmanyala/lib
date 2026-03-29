from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from django.db.models import F
from tinymce.models import HTMLField
from custom_user.models import User

# Create your models here.



class CpaSubject(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=500, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

class CpaPaper(models.Model):
    year = models.IntegerField()
    subject = models.ForeignKey(CpaSubject, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    month = models.CharField(max_length=100)

    

class CpaQuestions(models.Model):
    year = models.IntegerField()
    subject = models.ForeignKey(CpaSubject, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    month = models.CharField(max_length=100)
    question = HTMLField()
    answer = HTMLField(blank=True, null=True)
    paper = models.ForeignKey(CpaPaper, on_delete=models.CASCADE)


