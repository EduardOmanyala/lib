from rest_framework import serializers
from .models import CpaPaper, CpaQuestions, ContactMessage


class CpaPaperSerializer(serializers.ModelSerializer):
    subject_title = serializers.CharField(source='subject.title', read_only=True)
    subject_slug = serializers.CharField(source='subject.slug', read_only=True)

    class Meta:
        model = CpaPaper
        fields = ['id', 'year', 'month', 'course', 'subject_title', 'subject_slug']


class CpaQuestionSerializer(serializers.ModelSerializer):
    subject_title = serializers.CharField(source='subject.title', read_only=True)

    class Meta:
        model = CpaQuestions
        fields = [
            'id',
            'year',
            'month',
            'course',
            'subject_title',
            'question',
            'answer',
            'paper'
        ]





class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'