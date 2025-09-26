from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from questions import views as questions_views

urlpatterns = [
    path('', questions_views.home, name='home'),
    path('sample', questions_views.sample, name='sample-home'),
    path('cpa', questions_views.cpa, name='cpa-home'),
    path('questions/', questions_views.questions_list, name='questions-list'),
    path('books/', questions_views.books_list, name='books-list'),
    path("fix/", questions_views.generate_fixture2, name="generate_fixture"),
    path("questions/get/", questions_views.QuestionFetchView.as_view(), name="questions-fecth"),
    path("questions/random/", questions_views.random_questions, name="random-questions"),
    path("test/", questions_views.test_endpoint, name="test-endpoint"),


    path("books/<int:id>/", questions_views.BookDetailView.as_view(), name="book-detail"),
    path("books/pay/<int:id>/", questions_views.payView, name="book-pay"),
    path("books/pay/callback/", questions_views.pay_success, name="book-pay-success"),
    
    # API endpoints for courses and subjects
    path('api/courses/', questions_views.course_list, name='course_list'),
    path('api/courses/<int:course_id>/', questions_views.course_detail, name='course_detail'),
    path('api/courses/<int:course_id>/subjects/', questions_views.subjects_by_course, name='subjects_by_course'),
    
    # User's courses and subjects
    path('api/my-courses/', questions_views.my_courses, name='my_courses'),
    path('api/my-courses/<int:course_id>/remove/', questions_views.remove_my_course, name='remove_my_course'),
    path('api/my-subjects/', questions_views.my_subjects, name='my_subjects'),
    path('api/my-subjects/<int:subject_id>/remove/', questions_views.remove_my_subject, name='remove_my_subject'),
    path('api/dashboard-data/', questions_views.user_dashboard_data, name='user_dashboard_data'),
    path('api/onboarding-status/', questions_views.check_onboarding_status, name='check_onboarding_status'),


    path('mailtest', questions_views.mailtest1, name='mailtest'),
]



