from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Resume, CoverLetter
from .serializers import ResumeSerializer, CoverLetterSerializer

class UploadResumeView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        resume = Resume.objects.create(
            file=file,
            original_filename=file.name
        )

        return Response({
            'url': resume.file.url,
            'filename': resume.original_filename
        }, status=status.HTTP_201_CREATED)

class UploadCoverLetterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = CoverLetter.objects.all()
    serializer_class = CoverLetterSerializer

    def create(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        cover_letter = CoverLetter.objects.create(
            file=file,
            original_filename=file.name
        )

        return Response({
            'url': cover_letter.file.url,
            'filename': cover_letter.original_filename
        }, status=status.HTTP_201_CREATED)
