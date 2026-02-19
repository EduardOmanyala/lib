from django.shortcuts import render, redirect
from questions.models import Question, Kasneb, Book, Docs, Webhook, MMFProvider, MMFMonthlyRate
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics, status
from questions.serializers import QuestionSerializer, BookSerializer, MMFProviderSerializer, MMFMonthlyRateSerializer
from django.contrib import messages
import random





from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.shortcuts import get_object_or_404
import json

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



def generate_fixture(request):
    # html_file = os.path.join(settings.BASE_DIR, "data.html")
    html_file = os.path.join(settings.BASE_DIR, "questions", "fixtures", "unserailized", "2018", "physicsp2.html")
    output_path = os.path.join(settings.BASE_DIR, "questions", "fixtures","fixture.json")

    # Parse HTML
    with open(html_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    divs = soup.find_all("div", id="qdiv")

    # Default pk start
    start_pk = 1

    # If fixture file exists, load it and find the last pk
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            if existing_data:
                last_pk = max(item["pk"] for item in existing_data)
                start_pk = last_pk + 1
    else:
        existing_data = []

    # Build new fixtures
    new_fixtures = []
    for i, div in enumerate(divs, start=start_pk):
        new_fixtures.append({
            "model": "questions.Question",
            "pk": i,
            "fields": {
                "year": 2018,
                "subject": "Physics",
                "type": "kcse",
                "paper_type": 2,
                "question_num": 1,
                "text": div.decode_contents().strip()
            }
        })

    # Append to existing fixtures
    fixtures = existing_data + new_fixtures

    # Save JSON back
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2, ensure_ascii=False)
    messages.success(request, f"✅ Added {len(new_fixtures)} items starting at pk={start_pk}")
    return redirect('home')
    #return HttpResponse(f"✅ Added {len(new_fixtures)} items starting at pk={start_pk}")



def generate_fixture2(request):
    # Input folder (contains html files, possibly with subfolders)
    input_folder = os.path.join(settings.BASE_DIR, "questions", "fixtures", "unserailized", "2023")
    output_path = os.path.join(settings.BASE_DIR, "questions", "fixtures", "kcse.json")

    # Default pk start
    start_pk = 1

    # If fixture file exists, load it and find the last pk
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
            if existing_data:
                last_pk = max(item["pk"] for item in existing_data)
                start_pk = last_pk + 1
    else:
        existing_data = []

    fixtures = existing_data[:]
    pk_counter = start_pk

    # Walk over all HTML files in folder (including subfolders)
    for root, _, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".html"):
                html_file = os.path.join(root, filename)

                with open(html_file, "r", encoding="utf-8") as f:
                    soup = BeautifulSoup(f, "html.parser")

                # Extract metadata from <script>
                script_tag = soup.find("script")
                subject = None
                year = None
                paper_type = None

                if script_tag and script_tag.string:
                    # crude parsing, assuming lines like: subject = "Physics"
                    for line in script_tag.string.splitlines():
                        line = line.strip().replace("“", '"').replace("”", '"')
                        if line.startswith("subject"):
                            subject = line.split("=")[1].strip().strip('"')
                        elif line.startswith("year"):
                            year = int(line.split("=")[1].strip().strip('"'))
                        elif line.startswith("paper_type"):
                            paper_type = int(line.split("=")[1].strip())

                # Fallback if script missing
                if not (subject and year and paper_type):
                    messages.warning(request, f"⚠️ Skipped {filename} (missing metadata)")
                    continue

                # Extract all questions
                divs = soup.find_all("div", id="qdiv")

                for div in divs:
                    fixtures.append({
                        "model": "questions.Question",
                        "pk": pk_counter,
                        "fields": {
                            "year": year,
                            "subject": subject,
                            "type": "kcse",
                            "paper_type": paper_type,
                            "question_num": 1,  # you may want to auto-increment this?
                            "text": div.decode_contents().strip()
                        }
                    })
                    pk_counter += 1

    # Save JSON back
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(fixtures, f, indent=2, ensure_ascii=False)

    messages.success(request, f"✅ Added {pk_counter - start_pk} questions across multiple files (starting at pk={start_pk})")
    return redirect('home')


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



@csrf_exempt  # Flutterwave won't send CSRF tokens
@require_POST
def payView(request, id):
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"message": "Invalid JSON"}, status=200)  # still 200

    # Get payment status and email from metadata
    status = data.get("status")
    metadata = data.get("meta") or data.get("metadata", {})
    user_email = metadata.get("email")

    # Always return 200 so Flutterwave knows we received it
    if status != "successful" or not user_email:
        return JsonResponse({"message": "Payment not successful or email missing"}, status=200)

    # Get the Book instance by id
    book = get_object_or_404(Book, id=id)

    # Prepare email
    subject = f"Your Purchase: {book.title}"
    html_message = render_to_string("questions/booksale.html", {"book": book})
    email = EmailMessage(
        subject=subject,
        body=html_message,
        from_email="noreply@yourdomain.com",
        to=[user_email],
    )
    email.content_subtype = "html"

    # Attach PDF file
    if book.pdf_file:
        email.attach_file(book.pdf_file.path)

    # Try sending email (but still return 200 no matter what)
    try:
        email.send()
    except Exception as e:
        # log error here if you want
        return JsonResponse({"message": f"Error sending email: {str(e)}"}, status=200)

    return JsonResponse({"message": "Email sent successfully"}, status=200)


from django.core.mail import EmailMessage, send_mail
def mailtest1(request):
    send_mail('Using SparkPost with Django123', 'This is a message from Django using SparkPost!123', 'Northstar@the-northstar.com',
    ['bestessays001@gmail.com'], fail_silently=False)
    return redirect('home')




@csrf_exempt
def pay_success(request):
    """
    Webhook to handle Flutterwave payment success.
    """
    if request.method == "POST":
        try:
            payload = json.loads(request.body)

            # Always return 200 to Flutterwave
            response = HttpResponse(status=200)

            # ✅ Only continue if payment is successful
            if payload.get("status") != "successful":
                return response

            # Extract tx_ref → format book-<id>-<uuid>
            tx_ref = payload.get("tx_ref", "")
            book_id = None
            if tx_ref.startswith("book-"):
                parts = tx_ref.split("-")
                if len(parts) >= 2:
                    book_id = parts[1]

            # Extract email from meta or customer
            email = None
            meta = payload.get("meta", {})
            if isinstance(meta, dict):
                email = meta.get("email") or payload.get("customer", {}).get("email")

            # If we have both book_id and email, continue
            if book_id and email:
                try:
                    book = Book.objects.get(id=book_id)

                    # Prepare email
                    subject = f"Your Book: {book.title}"
                    html_message = render_to_string("questions/booksale.html", {"book": book})

                    message = EmailMessage(
                        subject=subject,
                        body=html_message,
                        from_email="Northstar@the-northstar.com",
                        to=[email],
                    )
                    message.content_subtype = "html"


                    docs = Docs.objects.filter(book=book)

                    # Attach each doc file (if available)
                    for doc in docs:
                        if doc.file and doc.file.path:  # ensure file exists
                            message.attach_file(doc.file.path)

                    # Attach book PDF if available
                    # if book.pdf:
                    #     message.attach_file(book.pdf.path)

                    message.send(fail_silently=False)

                except Book.DoesNotExist:
                    pass  # Optionally log error

            return response

        except Exception as e:
            # Log the error in production
            return HttpResponse(status=200)

    return HttpResponse(status=405)



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
    
