from django.db import models
from django.utils.text import slugify
from django.db.models.signals import pre_save
from tinymce.models import HTMLField
from custom_user.models import User

# Create your models here.

class Question(models.Model):
    year = models.IntegerField(db_index=True)
    subject = models.CharField(max_length=100, db_index=True)
    type = models.CharField(max_length=50, db_index=True)
    text = HTMLField()
    question_num = models.IntegerField()
    PAPER_TYPE_CHOICES = (
        (1, 'Paper 1'),
        (2, 'Paper 2'),
        (3, 'Paper 3'),
    )
    paper_type = models.IntegerField(choices=PAPER_TYPE_CHOICES, blank=True, null=True)
    image = models.ImageField(upload_to ='questionimages/', blank=True, null=True)
    explanation = HTMLField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.subject} - Question {self.question_num} ({self.year})"
    
    class Meta:
        ordering = ['year', 'subject', 'question_num']



class Kasneb(models.Model):
    year = models.IntegerField()
    subject = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    month = models.CharField(max_length=100)
    text = HTMLField()
    ans = HTMLField(blank=True, null=True)


# Course and Subject Models
class Course(models.Model):
    COURSE_CHOICES = [
        ('kcse', 'KCSE'),
        ('cpa', 'CPA/CPS'),
        ('kmtc', 'KMTC'),
        ('acca', 'ACCA'),
    ]
    
    code = models.CharField(max_length=10, choices=COURSE_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']


class Subject(models.Model):
    SUBJECT_CHOICES = [
        # KCSE Subjects
        ('mathematics', 'Mathematics'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('english', 'English'),
        ('kiswahili', 'Kiswahili'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('computer_studies', 'Computer Studies'),
        ('business_studies', 'Business Studies'),
        ('agriculture', 'Agriculture'),
        
        # CPA Subjects
        ('financial_accounting', 'Financial Accounting'),
        ('auditing', 'Auditing'),
        
        # KMTC Subjects (placeholder - you can add specific subjects)
        ('nursing', 'Nursing'),
        ('clinical_medicine', 'Clinical Medicine'),
        ('pharmacy', 'Pharmacy'),
        
        # ACCA Subjects (placeholder - you can add specific subjects)
        ('financial_accounting_acc', 'Financial Accounting'),
        ('management_accounting', 'Management Accounting'),
        ('audit_assurance', 'Audit & Assurance'),
    ]
    
    code = models.CharField(max_length=50, choices=SUBJECT_CHOICES, unique=True)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    
    def __str__(self):
        return f"{self.name} ({self.course.name})"
    
    class Meta:
        ordering = ['course', 'name']


class MyCourses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_courses')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - {self.course.name}"
    
    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-created_at']


class MySubjects(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='my_subjects')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='user_subjects')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='user_subjects')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.subject.name} ({self.course.name})"

    class Meta:
        unique_together = ['user', 'subject']
        ordering = ['-created_at']


class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=200)
    price = models.IntegerField(default=180)
    availability = models. BooleanField(default=False)
    pdf_file = models.FileField(upload_to='books/')
    created_at = models.DateTimeField(auto_now_add=True)
    purchase_count = models.IntegerField(default=0)
    info = HTMLField(null=True, blank=True)
    summary = models.TextField(blank=True, null=True)
    pdf = models.FileField(upload_to='books/', null=True, blank=True)
    slug = models.SlugField(max_length=500, unique=True, blank=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

    class Meta:
        ordering = ['-created_at']


def create_book_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)

pre_save.connect(create_book_slug, sender=Book)


class Docs(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    file = models.FileField(upload_to='books/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Webhook(models.Model):
    raw_payload = models.JSONField()           # ← this stores the FULL original JSON


