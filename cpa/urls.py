from django.urls import path
from cpa import views as cpa_views

urlpatterns = [
    path('cpa/papers/<slug:slug>/', cpa_views.papers_by_subject),
    path('cpa/questions/<int:paper_id>/', cpa_views.QuestionsByPaperView.as_view(), name='questions-by-paper'),
]