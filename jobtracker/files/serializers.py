from rest_framework import serializers
from .models import Resume, CoverLetter

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ['id', 'file', 'uploaded_at', 'original_filename']
        read_only_fields = ['uploaded_at', 'original_filename']

class CoverLetterSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverLetter
        fields = ['id', 'file', 'uploaded_at', 'original_filename']
        read_only_fields = ['uploaded_at', 'original_filename']