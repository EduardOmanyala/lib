from django.urls import path
from cpa import views as cpa_views

urlpatterns = [
    path('cpa/papers/<slug:slug>/', cpa_views.papers_by_subject),
    path('cpa/questions/<int:paper_id>/', cpa_views.QuestionsByPaperView.as_view(), name='questions-by-paper'),
    path('api/contact/', cpa_views.contact_message_create, name='contact-message'),
    path('posts/', cpa_views.PostsListView.as_view(), name='posts'),
    path('posts/<int:id>/<slug:slug>/', cpa_views.SinglePostView.as_view(), name='single-post'),
]