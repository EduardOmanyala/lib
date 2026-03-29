from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.generics import ListAPIView
from .models import CpaPaper, CpaQuestions
from .serializers import CpaPaperSerializer, CpaQuestionSerializer





@api_view(['GET'])
@permission_classes([AllowAny])
def papers_by_subject(request, slug):
    papers = CpaPaper.objects.filter(subject__slug=slug).select_related('subject')
    serializer = CpaPaperSerializer(papers, many=True)
    return Response(serializer.data)

class QuestionsByPaperView(ListAPIView):
    serializer_class = CpaQuestionSerializer
    permission_classes = [AllowAny] 

    def get_queryset(self):
        paper_id = self.kwargs['paper_id']
        return CpaQuestions.objects.filter(paper_id=paper_id)