from django.shortcuts import render, redirect
from questions.models import (Question, Kasneb, Book, Docs, Webhook, 
                              MMFProvider, MMFMonthlyRate, 
                              Purchases, MyNotifications, 
                              PaymentLog,
                              SFProvider,
                              SFMonthlyRate,
                             )
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from questions.serializers import (QuestionSerializer, BookSerializer, 
                                   MMFProviderSerializer, MMFMonthlyRateSerializer, 
                                   NotificationSerializer,
                                   SFMonthlyRateSerializer,
                                   SFProviderSerializer,
                                   SFRateSummarySerializer)
from django.contrib import messages
from custom_user.models import User
from django.db import transaction
import random
from .tasks import send_test_email, send_book_email
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
import json
# views.py
import os

import re
from bs4 import BeautifulSoup
from django.http import HttpResponse
from django.conf import settings

# views.py

import zipfile
from django.http import FileResponse, Http404
from tempfile import NamedTemporaryFile
import logging




logger = logging.getLogger(__name__)

# Create your views here.



def home(request):
    questions = Question.objects.all()[:5]
    books = Book.objects.all()
    return render(request, 'questions/home.html', {'questions': questions, 'books': books})


def cpa(request):
    questions = Kasneb.objects.filter().order_by('id')[:5]
    return render(request, 'questions/cpa.html', {'questions': questions})

def sample(request):
    return render(request, 'questions/sample.html')


@api_view(['GET'])
@permission_classes([AllowAny])
def questions_list(request):
    print("Questions list view accessed - no authentication required")
    questions = Question.objects.all()
    serializer = QuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def books_list(request):
    print("Books list view accessed - no authentication required")
    #books = Book.objects.all()
    books = Book.objects.filter(availability=True)
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

class BookDetailView(generics.RetrieveAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    lookup_field = "id" 
    permission_classes = [AllowAny]  # so URL can use /books/<id>/

@api_view(['GET'])
@permission_classes([AllowAny])
def test_endpoint(request):
    print("Test endpoint accessed - no authentication required")
    return Response({"message": "Test endpoint working - no auth required"})

class QuestionFetchView(generics.ListAPIView):
    serializer_class = QuestionSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        print(f"Question fetch request received: {self.request.query_params}")
        
        queryset = Question.objects.all()
        print(f"Initial queryset count: {queryset.count()}")

        year = self.request.query_params.get('year')
        subject = self.request.query_params.get('subject')
        q_type = self.request.query_params.get('type')
        paper_type = self.request.query_params.get('paper_type')

        print(f"Filters - Year: {year}, Subject: {subject}, Type: {q_type}, Paper Type: {paper_type}")

        if year:
            queryset = queryset.filter(year=year)
        if subject:
            queryset = queryset.filter(subject__icontains=subject)
        if q_type:
            queryset = queryset.filter(type=q_type)
        if paper_type:
            queryset = queryset.filter(paper_type=paper_type)

        print(f"Filtered queryset count: {queryset.count()}")

        # Limit to 50 questions maximum
        queryset = queryset[:50]
        
        print(f"Returning {queryset.count()} questions")
        return queryset



import os
import json
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from bs4 import BeautifulSoup
from .models import Course, Subject, MyCourses, MySubjects
from .serializers import (
    QuestionSerializer, KasnebSerializer, CourseSerializer, SubjectSerializer,
    MyCoursesSerializer, MySubjectsSerializer, CourseWithSubjectsSerializer
)




@api_view(['GET'])
@permission_classes([AllowAny])
def random_questions(request):
    """
    Efficiently fetch random questions by subject and paper_type.
    Uses Python random module instead of Django's random query for better performance.
    """
    print("Random questions view accessed")
    
    # Get query parameters
    subject = request.query_params.get('subject')
    paper_type = request.query_params.get('paper_type')
    count = request.query_params.get('count', 10)
    
    # Validate required parameters
    if not subject:
        return Response({'error': 'Subject is required'}, status=400)
    
    try:
        count = int(count)
        if count not in [5, 10, 15, 20]:
            return Response({'error': 'Count must be 5, 10, 15, or 20'}, status=400)
    except ValueError:
        return Response({'error': 'Invalid count parameter'}, status=400)
    
    # Build efficient query
    queryset = Question.objects.filter(
        subject__icontains=subject,
        type='kcse'  # Default type
    )
    
    # Add paper_type filter if provided
    if paper_type:
        try:
            paper_type = int(paper_type)
            queryset = queryset.filter(paper_type=paper_type)
        except ValueError:
            return Response({'error': 'Invalid paper_type parameter'}, status=400)
    
    print(f"Filtered queryset count: {queryset.count()}")
    
    # Convert to list for random selection
    questions_list = list(queryset)
    
    if not questions_list:
        return Response({'error': 'No questions found for the specified criteria'}, status=404)
    
    # Randomly select questions
    selected_questions = random.sample(questions_list, min(count, len(questions_list)))
    
    # Serialize the selected questions
    serializer = QuestionSerializer(selected_questions, many=True)
    
    print(f"Returning {len(selected_questions)} random questions")
    return Response(serializer.data)


# API Views for Course and Subject Management
@api_view(['GET'])
def course_list(request):
    """Get all available courses"""
    courses = Course.objects.all()
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def course_detail(request, course_id):
    """Get a specific course with its subjects"""
    try:
        course = Course.objects.get(id=course_id)
        serializer = CourseWithSubjectsSerializer(course)
        return Response(serializer.data)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def subjects_by_course(request, course_id):
    """Get all subjects for a specific course"""
    try:
        subjects = Subject.objects.filter(course_id=course_id)
        serializer = SubjectSerializer(subjects, many=True)
        return Response(serializer.data)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_courses(request):
    """Get user's selected courses or add a new course"""
    if request.method == 'GET':
        my_courses = MyCourses.objects.filter(user=request.user)
        serializer = MyCoursesSerializer(my_courses, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Check if user already has this course
        course_id = request.data.get('course')
        if MyCourses.objects.filter(user=request.user, course_id=course_id).exists():
            return Response({'error': 'Course already selected'}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = MyCoursesSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_my_course(request, course_id):
    """Remove a course from user's selection"""
    try:
        my_course = MyCourses.objects.get(user=request.user, course_id=course_id)
        my_course.delete()
        return Response({'message': 'Course removed successfully'}, status=status.HTTP_204_NO_CONTENT)
    except MyCourses.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def my_subjects(request):
    """Get user's selected subjects or add new subjects"""
    if request.method == 'GET':
        my_subjects = MySubjects.objects.filter(user=request.user)
        serializer = MySubjectsSerializer(my_subjects, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        # Handle multiple subjects
        subjects_data = request.data
        if not isinstance(subjects_data, list):
            subjects_data = [subjects_data]
        
        created_subjects = []
        errors = []
        
        for subject_data in subjects_data:
            # Check if user already has this subject
            subject_id = subject_data.get('subject')
            if MySubjects.objects.filter(user=request.user, subject_id=subject_id).exists():
                errors.append(f'Subject {subject_id} already selected')
                continue
            
            serializer = MySubjectsSerializer(data=subject_data)
            if serializer.is_valid():
                subject = serializer.save(user=request.user)
                created_subjects.append(serializer.data)
            else:
                errors.append(serializer.errors)
        
        if created_subjects:
            return Response({
                'created': created_subjects,
                'errors': errors
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_my_subject(request, subject_id):
    """Remove a subject from user's selection"""
    try:
        my_subject = MySubjects.objects.get(user=request.user, subject_id=subject_id)
        my_subject.delete()
        return Response({'message': 'Subject removed successfully'}, status=status.HTTP_204_NO_CONTENT)
    except MySubjects.DoesNotExist:
        return Response({'error': 'Subject not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard_data(request):
    """Get user's courses and subjects for dashboard"""
    my_courses = MyCourses.objects.filter(user=request.user)
    my_subjects = MySubjects.objects.filter(user=request.user)
    
    courses_serializer = MyCoursesSerializer(my_courses, many=True)
    subjects_serializer = MySubjectsSerializer(my_subjects, many=True)
    
    return Response({
        'courses': courses_serializer.data,
        'subjects': subjects_serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_onboarding_status(request):
    """Check if user has completed onboarding (selected courses)"""
    has_courses = MyCourses.objects.filter(user=request.user).exists()
    has_subjects = MySubjects.objects.filter(user=request.user).exists()
    
    return Response({
        'has_courses': has_courses,
        'has_subjects': has_subjects,
        'onboarding_complete': has_courses and has_subjects
    })


from django.core.mail import EmailMessage, send_mail
# def mailtest1(request):
#     send_mail('Using SparkPost with Django123', 'This is a message from Django using SparkPost!123', 'Kenlib@ken-lib.com',
#     ['bestessays001@gmail.com'], fail_silently=False)
#     return redirect('home')



def mailtest1(request):
    send_test_email.delay()   # ← runs asynchronously via Celery
    return redirect('home')

def mailtest2(request):
    send_mail(
        'Using SparkPost with Django123',
        'This is a message from Django using SparkPost!123',
        'Kenlib@ken-lib.com',
        ['bestessays001@gmail.com'],
        fail_silently=False
    )
    return redirect('home')


    
@csrf_exempt
def pay_success(request):
    try:
        payload = json.loads(request.body)

        # Only process relevant events
        if payload.get("event") != "charge.completed":
            return HttpResponse(status=200)

        data = payload.get("data", {})

        # Only process successful payments
        if data.get("status") != "successful":
            return HttpResponse(status=200)

        tx_ref = data.get("tx_ref")
        if not tx_ref:
            logger.warning("Missing tx_ref")
            return HttpResponse(status=200)

        # جلوگی
        if PaymentLog.objects.filter(tx_ref=tx_ref).exists():
            return HttpResponse(status=200)

        parts = tx_ref.split("-")

        if len(parts) < 4 or parts[0] != "book":
            logger.warning(f"Invalid tx_ref format: {tx_ref}")
            return HttpResponse(status=200)

        book_id = parts[1]
        user_id = parts[2]

        with transaction.atomic():
            book = Book.objects.get(id=book_id)
            user = User.objects.get(id=user_id)

            email = user.email

            # Validate amount (don’t trust gateway blindly)
            if data.get("amount") != book.price:
                logger.warning("Amount mismatch")
                return HttpResponse(status=200)

            # Prevent duplicate purchase
            purchase, created = Purchases.objects.get_or_create(
                book=book,
                user=user
            )

            if created:
                book.purchase_count += 1
                book.save()

            #send_book_email.delay(book.id, email)

            # Log processed payment
            PaymentLog.objects.create(tx_ref=tx_ref)

    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")

    # ALWAYS return 200
    return HttpResponse(status=200)






@csrf_exempt
@require_POST
def flutterwave_webhook(request):
    # Step 1: Get the raw body exactly as Flutterwave sent it
    try:
        raw_body = request.body.decode('utf-8')  # or just keep as bytes if you prefer
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        # Bad JSON → still return 200 so Flutterwave doesn't retry endlessly
        return JsonResponse({"status": "invalid json"}, status=200)

    # Step 2: Save the FULL raw payload immediately
    webhook = Webhook.objects.create(
        raw_payload=payload
    )

    # Step 5: Always return 200 OK quickly
    return JsonResponse({"status": "success"}, status=200)



def webhook_test(request):
    webhooks = Webhook.objects.all()[:5]
    payloads = [
        json.dumps(w.raw_payload, indent=2)
        for w in webhooks
    ]
   
    return render(request, 'questions/webhooks.html', {'payloads': payloads})


def getway_test(request):
      
      return render(request, 'questions/fluter.html')


class MMFProviderDetailView(APIView):
    permission_classes = [AllowAny]
    """
    Returns:
    - Provider name
    - Last 12 monthly rates
    - Latest rate
    - Percentage change from previous month
    """
    
    def get(self, request, code):
        try:
            provider = MMFProvider.objects.get(code=code, is_active=True)
        except MMFProvider.DoesNotExist:
            return Response(
                {"detail": "Provider not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Last 12 months (latest first, then reversed for chart)
        monthly_qs = (
            MMFMonthlyRate.objects
            .filter(provider=provider)
            .order_by("-created_at")[:12]
        )

        monthly_rates = list(monthly_qs)[::-1]

        latest = monthly_qs.first()

        return Response({
            "provider": MMFProviderSerializer(provider).data,
            "monthly_rates": MMFMonthlyRateSerializer(
                monthly_rates, many=True
            ).data,
            "latest_rate": latest.rate if latest else None,
            "percentage_change": (
                latest.percentage_change if latest else None
            ),
        })



 
class SFProviderDetailView(APIView):
    permission_classes = [AllowAny]
 
    
    def get(self, request, code):
        try:
            provider = SFProvider.objects.get(code=code, is_active=True)
        except SFProvider.DoesNotExist:
            return Response(
                {"detail": "Provider not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Last 12 months (latest first, then reversed for chart)
        monthly_qs = (
            SFMonthlyRate.objects
            .filter(provider=provider)
            .order_by("-created_at")[:12]
        )

        sfmonthly_rates = list(monthly_qs)[::-1]

        latest = monthly_qs.first()

        return Response({
            "provider": SFProviderSerializer(provider).data,
            "sfmonthly_rates": SFMonthlyRateSerializer(
                sfmonthly_rates, many=True
            ).data,
            "latest_rate": latest.rate if latest else None,
            "percentage_change": (
                latest.percentage_change if latest else None
            ),
        })
       




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def has_purchased(request, book_id):
    user = request.user

    exists = Purchases.objects.filter(user=user, book_id=book_id).exists()

    return Response({
        "purchased": exists
    }, status=status.HTTP_200_OK)



    

def generate_fixtures(request):

    data_folder = os.path.join(settings.BASE_DIR, 'questions', 'fixtures', 'collections')
    output_file = os.path.join(settings.BASE_DIR, 'questions', 'fixtures', 'cpa.json')
    model_name = "cpa.CpaQuestions"

    fixtures = []
    pk_counter = 1

    for filename in os.listdir(data_folder):
        if filename.endswith('.html'):
            html_file_path = os.path.join(data_folder, filename)

            with open(html_file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # --- EXTRACT CONSTANTS FROM SCRIPT ---
            script_tag = soup.find('script')
            script_text = script_tag.get_text() if script_tag else ""

            year_match = re.search(r'year\s*=\s*"(\d+)"', script_text)
            course_match = re.search(r'course\s*=\s*"([^"]+)"', script_text)
            month_match = re.search(r'month\s*=\s*"([^"]+)"', script_text)

            # ✅ SUBJECT: must be integer (FK)
            subject_int_match = re.search(r'subject\s*=\s*(\d+)', script_text)
            subject_str_match = re.search(r'subject\s*=\s*"([^"]+)"', script_text)

            if subject_str_match:
                raise ValueError(f"ERROR in {filename}: subject should be INTEGER FK, found string '{subject_str_match.group(1)}'")

            if not subject_int_match:
                raise ValueError(f"ERROR in {filename}: subject not found or invalid format")

            subject = int(subject_int_match.group(1))

            # ✅ PAPER (already correct)
            paper_match = re.search(r'paper\s*=\s*(\d+)', script_text)
            if not paper_match:
                raise ValueError(f"ERROR in {filename}: paper not found")

            paper = int(paper_match.group(1))

            # --- other fields ---
            year = int(year_match.group(1)) if year_match else 0
            course = course_match.group(1) if course_match else ""
            month = month_match.group(1) if month_match else ""

            # ✅ NEW: assign paper
            paper = int(paper_match.group(1)) if paper_match else None

            # --- FIND ALL Q&A PAIRS ---
            q_divs = soup.find_all('div', id='qdiv')
            a_divs = soup.find_all('div', id='ansdiv')

            if len(q_divs) != len(a_divs):
                print(f"Warning in {filename}: Number of questions and answers do not match!")

            for qdiv, ansdiv in zip(q_divs, a_divs):
                fixture = {
                    "model": model_name,
                    "pk": pk_counter,
                    "fields": {
                        "year": year,
                        "subject": subject,
                        "course": course,
                        "month": month,
                        "paper": paper,  # ✅ NEW FIELD
                        "question": str(qdiv),
                        "answer": str(ansdiv)
                    }
                }
                fixtures.append(fixture)
                pk_counter += 1

    # --- WRITE TO JSON FILE ---
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=2)

    return HttpResponse(f"Fixture generated with {len(fixtures)} questions at {output_file}")



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_book(request, book_id):
    user = request.user

    # ✅ Check purchase
    has_purchased = Purchases.objects.filter(
        user=user, book_id=book_id
    ).exists()

    if not has_purchased:
        raise Http404("You have not purchased this book")

    docs = Docs.objects.filter(book_id=book_id)

    if not docs.exists():
        raise Http404("No files found")

    # ✅ If only ONE file → return directly
    if docs.count() == 1:
        file_path = docs.first().file.path
        # return FileResponse(open(file_path, 'rb'), as_attachment=True)
        filename = os.path.basename(file_path)
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=filename
)
    # ✅ If MULTIPLE → zip them
    temp_zip = NamedTemporaryFile(delete=False, suffix=".zip")

    with zipfile.ZipFile(temp_zip.name, 'w') as zipf:
        for doc in docs:
            if doc.file:
                file_path = doc.file.path
                filename = os.path.basename(file_path)
                zipf.write(file_path, filename)

    return FileResponse(
        open(temp_zip.name, 'rb'),
        as_attachment=True,
        filename=f"book_{book_id}.zip"
    )


# 🔔 Fetch all unread notifications
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_unread_notifications(request):
    notifications = MyNotifications.objects.filter(
        user=request.user,
        read=False
    ).order_by('-created_at')

    serializer = NotificationSerializer(notifications, many=True)
    return Response(serializer.data)

# ✅ Mark all unread notifications as read
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_notifications_as_read(request):
    updated_count = MyNotifications.objects.filter(
        user=request.user,
        read=False
    ).update(read=True)

    return Response({
        "message": "Notifications marked as read",
        "updated": updated_count
    })

# 🔔 Fetch all unread notifications
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_notifications(request):
    allnotifications = MyNotifications.objects.filter(user=request.user).order_by('-created_at')[:5]
    serializer = NotificationSerializer(allnotifications, many=True)
    return Response(serializer.data)
