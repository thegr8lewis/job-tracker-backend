# from rest_framework import serializers
# from .models import Application, TimelineEvent
# from django.utils import timezone

# class TimelineEventSerializer(serializers.ModelSerializer):
#     date = serializers.DateField(format="%Y-%m-%d")
    
#     class Meta:
#         model = TimelineEvent
#         fields = ['id', 'event_type', 'title', 'description', 'date', 'completed', 'created_at']
#         read_only_fields = ('created_at',)

# class ApplicationSerializer(serializers.ModelSerializer):
#     timeline_events = TimelineEventSerializer(many=True, read_only=True)
    
#     class Meta:
#         model = Application
#         fields = [
#             'id', 'company_name', 'job_title', 'job_posting_url', 'location',
#             'salary_range', 'application_date', 'status', 'notes', 'resume',
#             'cover_letter', 'created_at', 'updated_at', 'timeline_events'
#         ]
#         read_only_fields = ('created_at', 'updated_at')

# class CreateApplicationSerializer(serializers.ModelSerializer):
#     application_date = serializers.DateField(
#         required=False, 
#         default=timezone.now().date,
#         input_formats=['%Y-%m-%d']
#     )
#     status = serializers.CharField(
#         required=False, 
#         default='applied'
#     )

#     class Meta:
#         model = Application
#         fields = [
#             'company_name', 'job_title', 'job_posting_url', 'location',
#             'salary_range', 'application_date', 'status', 'notes',
#             'resume', 'cover_letter'
#         ]
#         extra_kwargs = {
#             'resume': {'required': False, 'allow_null': True},
#             'cover_letter': {'required': False, 'allow_null': True},
#             'job_posting_url': {'required': False, 'allow_blank': True},
#             'location': {'required': False, 'allow_blank': True},
#             'salary_range': {'required': False, 'allow_blank': True},
#             'notes': {'required': False, 'allow_blank': True},
#         }

# class UpdateApplicationSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Application
#         fields = [
#             'company_name', 'job_title', 'job_posting_url', 'location',
#             'salary_range', 'application_date', 'status', 'notes',
#             'resume', 'cover_letter'
#         ]
#         extra_kwargs = {
#             'company_name': {'required': False},
#             'job_title': {'required': False},
#             'resume': {'required': False, 'allow_null': True},
#             'cover_letter': {'required': False, 'allow_null': True},
#         }

# class UpdateStatusSerializer(serializers.Serializer):
#     status = serializers.CharField(max_length=20)

# class AddTimelineEventSerializer(serializers.ModelSerializer):
#     date = serializers.DateField(
#         required=False,
#         default=timezone.now().date,
#         input_formats=['%Y-%m-%d']
#     )
    
#     class Meta:
#         model = TimelineEvent
#         fields = ['event_type', 'title', 'description', 'date', 'completed']
#         extra_kwargs = {
#             'event_type': {'required': True},
#             'title': {'required': True},
#             'description': {'required': False},
#             'completed': {'required': False, 'default': False},
#         }





from rest_framework import serializers
from .models import Application, TimelineEvent
from django.utils import timezone

class TimelineEventSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y-%m-%d")
    
    class Meta:
        model = TimelineEvent
        fields = ['id', 'event_type', 'title', 'description', 'date', 'completed', 'created_at']
        read_only_fields = ('created_at',)

class ApplicationSerializer(serializers.ModelSerializer):
    timeline_events = TimelineEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id',
            'user_uid',
            'company_name', 'job_title', 'job_posting_url', 'location',
            'salary_range', 'application_date', 'status', 'notes', 'resume',
            'cover_letter', 'created_at', 'updated_at', 'timeline_events'
        ]
        read_only_fields = ('created_at', 'updated_at')

class CreateApplicationSerializer(serializers.ModelSerializer):
    user_uid = serializers.CharField(required=True)

    application_date = serializers.DateField(
        required=False, 
        default=timezone.now().date,
        input_formats=['%Y-%m-%d']
    )
    status = serializers.CharField(
        required=False, 
        default='applied'
    )

    class Meta:
        model = Application
        fields = [
            'user_uid',
            'company_name', 'job_title', 'job_posting_url', 'location',
            'salary_range', 'application_date', 'status', 'notes',
            'resume', 'cover_letter'
        ]
        extra_kwargs = {
            'resume': {'required': False, 'allow_null': True},
            'cover_letter': {'required': False, 'allow_null': True},
            'job_posting_url': {'required': False, 'allow_blank': True},
            'location': {'required': False, 'allow_blank': True},
            'salary_range': {'required': False, 'allow_blank': True},
            'notes': {'required': False, 'allow_blank': True},
        }

class UpdateApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            'company_name', 'job_title', 'job_posting_url', 'location',
            'salary_range', 'application_date', 'status', 'notes',
            'resume', 'cover_letter'
        ]
        extra_kwargs = {
            'company_name': {'required': False},
            'job_title': {'required': False},
            'resume': {'required': False, 'allow_null': True},
            'cover_letter': {'required': False, 'allow_null': True},
        }

class UpdateStatusSerializer(serializers.Serializer):
    status = serializers.CharField(max_length=20)

class AddTimelineEventSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        required=False,
        default=timezone.now().date,
        input_formats=['%Y-%m-%d']
    )
    
    class Meta:
        model = TimelineEvent
        fields = ['event_type', 'title', 'description', 'date', 'completed']
        extra_kwargs = {
            'event_type': {'required': True},
            'title': {'required': True},
            'description': {'required': False},
            'completed': {'required': False, 'default': False},
        }