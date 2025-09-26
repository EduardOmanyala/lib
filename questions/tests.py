from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from questions.models import Question
from tinymce.models import HTMLField

# Create your tests here.

class RandomQuestionsViewTest(APITestCase):
    def setUp(self):
        # Create some test questions
        Question.objects.create(
            year=2023,
            subject='Mathematics',
            type='kcse',
            paper_type=1,
            question_num=1,
            text='<p>Test question 1</p>'
        )
        Question.objects.create(
            year=2022,
            subject='Mathematics',
            type='kcse',
            paper_type=1,
            question_num=2,
            text='<p>Test question 2</p>'
        )
        Question.objects.create(
            year=2021,
            subject='Physics',
            type='kcse',
            paper_type=2,
            question_num=1,
            text='<p>Test physics question</p>'
        )

    def test_random_questions_with_subject(self):
        """Test random questions endpoint with subject parameter"""
        url = reverse('random-questions')
        response = self.client.get(url, {'subject': 'Mathematics', 'count': 2})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        
        # Check that all returned questions are Mathematics
        for question in response.data:
            self.assertEqual(question['subject'], 'Mathematics')

    def test_random_questions_with_subject_and_paper_type(self):
        """Test random questions endpoint with subject and paper_type parameters"""
        url = reverse('random-questions')
        response = self.client.get(url, {
            'subject': 'Mathematics', 
            'paper_type': 1, 
            'count': 1
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['subject'], 'Mathematics')
        self.assertEqual(response.data[0]['paper_type'], 1)

    def test_random_questions_missing_subject(self):
        """Test random questions endpoint without required subject parameter"""
        url = reverse('random-questions')
        response = self.client.get(url, {'count': 5})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_random_questions_invalid_count(self):
        """Test random questions endpoint with invalid count parameter"""
        url = reverse('random-questions')
        response = self.client.get(url, {'subject': 'Mathematics', 'count': 25})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_random_questions_no_results(self):
        """Test random questions endpoint when no questions match criteria"""
        url = reverse('random-questions')
        response = self.client.get(url, {'subject': 'Chemistry', 'count': 5})
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('error', response.data)
