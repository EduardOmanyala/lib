from rest_framework import serializers
from .models import (Question, Kasneb, Course, 
Subject, MyCourses, MySubjects, Book, 
Docs, MMFProvider, MMFMonthlyRate, 
MyNotifications, SFMonthlyRate, SFProvider)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'year', 'subject', 'type', 'paper_type', 'text', 'question_num']


class KasnebSerializer(serializers.ModelSerializer):
    class Meta:
        model = Kasneb
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'code', 'name']


class SubjectSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = Subject
        fields = ['id', 'code', 'name', 'course', 'course_name']


class MyCoursesSerializer(serializers.ModelSerializer):
    course_name = serializers.CharField(source='course.name', read_only=True)
    course_code = serializers.CharField(source='course.code', read_only=True)
    
    class Meta:
        model = MyCourses
        fields = ['id', 'course', 'course_name', 'course_code', 'created_at']
        read_only_fields = ['user', 'created_at']


class MySubjectsSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    subject_code = serializers.CharField(source='subject.code', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    
    class Meta:
        model = MySubjects
        fields = ['id', 'course', 'subject', 'subject_name', 'subject_code', 'course_name', 'created_at']
        read_only_fields = ['user', 'created_at']


class CourseWithSubjectsSerializer(serializers.ModelSerializer):
    subjects = SubjectSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = ['id', 'code', 'name', 'subjects']


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'pdf_file', 'created_at', 'availability', 'purchase_count', 'slug', 'price', 'info', 'adinfo', 'summary']

class DocsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Docs
        fields = ['id', 'file', 'created_at']


class MMFProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = MMFProvider
        fields = ["name", "code"]

class MMFMonthlyRateSerializer(serializers.ModelSerializer):
    month = serializers.CharField()
    rate = serializers.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = MMFMonthlyRate
        fields = ["month", "rate"]

class MMFRateSummarySerializer(serializers.Serializer):
    latest_rate = serializers.DecimalField(max_digits=6, decimal_places=2)
    percentage_change = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)


class NotificationSerializer(serializers.ModelSerializer):
    book_id = serializers.IntegerField(source='book.id', read_only=True)
    book_slug = serializers.CharField(source='book.slug', read_only=True)

    class Meta:
        model = MyNotifications
        fields = ['id', 'book', 'book_id', 'book_slug', 'text', 'read', 'created_at']




class SFProviderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SFProvider
        fields = ["name", "code"]

class SFMonthlyRateSerializer(serializers.ModelSerializer):
    month = serializers.CharField()
    rate = serializers.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        model = SFMonthlyRate
        fields = ["month", "rate"]

class SFRateSummarySerializer(serializers.Serializer):
    latest_rate = serializers.DecimalField(max_digits=6, decimal_places=2)
    percentage_change = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
