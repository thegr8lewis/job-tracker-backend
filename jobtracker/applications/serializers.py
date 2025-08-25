# from rest_framework import serializers
# from .models import Application, TimelineEvent, Job, JobFilter
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
#             'id',
#             'user_uid',
#             'company_name', 'job_title', 'job_posting_url', 'location',
#             'salary_range', 'application_date', 'status', 'notes', 'resume',
#             'cover_letter', 'created_at', 'updated_at', 'timeline_events'
#         ]
#         read_only_fields = ('created_at', 'updated_at')


# class CreateApplicationSerializer(serializers.ModelSerializer):
#     user_uid = serializers.CharField(required=True)
#     application_date = serializers.DateField(required=False, default=timezone.now().date, input_formats=['%Y-%m-%d'])
#     status = serializers.CharField(required=False, default='applied')

#     class Meta:
#         model = Application
#         fields = [
#             'user_uid',
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
#     date = serializers.DateField(required=False, default=timezone.now().date, input_formats=['%Y-%m-%d'])
#     class Meta:
#         model = TimelineEvent
#         fields = ['event_type', 'title', 'description', 'date', 'completed']
#         extra_kwargs = {
#             'event_type': {'required': True},
#             'title': {'required': True},
#             'description': {'required': False},
#             'completed': {'required': False, 'default': False},
#         }


# # ✅ Updated Job serializer
# class JobSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Job
#         fields = [
#             'id', 'title', 'company', 'location',
#             'salary_min', 'salary_max', 'link', 'source',
#             'posted_at', 'fetched_at'
#         ]


# # ✅ Filters
# class JobFilterSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = JobFilter
#         fields = [
#             'id', 'user_uid', 'keywords', 'locations',
#             'salary_min', 'remote_only', 'providers',
#             'created_at', 'updated_at'
#         ]
#         read_only_fields = ['created_at', 'updated_at']


from rest_framework import serializers
from .models import Application, TimelineEvent, Job, JobFilter
from django.utils import timezone
from functools import partial

# ---------------------------
# Timeline Event Serializer
# ---------------------------
class TimelineEventSerializer(serializers.ModelSerializer):
    date = serializers.DateField(format="%Y-%m-%d")

    class Meta:
        model = TimelineEvent
        fields = ['id', 'event_type', 'title', 'description', 'date', 'completed', 'created_at']
        read_only_fields = ('created_at',)


class AddTimelineEventSerializer(serializers.ModelSerializer):
    date = serializers.DateField(
        required=False,
        default=partial(lambda: timezone.localdate()),  # FIXED
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

# ---------------------------
# Application Serializers
# ---------------------------
class ApplicationSerializer(serializers.ModelSerializer):
    timeline_events = TimelineEventSerializer(many=True, read_only=True)

    class Meta:
        model = Application
        fields = [
            'id', 'user_uid', 'company_name', 'job_title',
            'job_posting_url', 'location', 'salary_range',
            'application_date', 'status', 'notes', 'resume',
            'cover_letter', 'created_at', 'updated_at', 'timeline_events'
        ]
        read_only_fields = ('created_at', 'updated_at')


class CreateApplicationSerializer(serializers.ModelSerializer):
    user_uid = serializers.CharField(required=True)
    application_date = serializers.DateField(
        required=False,
        default=partial(lambda: timezone.localdate()),
        input_formats=['%Y-%m-%d']
    )
    status = serializers.CharField(required=False, default='applied')

    class Meta:
        model = Application
        fields = [
            'user_uid', 'company_name', 'job_title', 'job_posting_url',
            'location', 'salary_range', 'application_date', 'status',
            'notes', 'resume', 'cover_letter'
        ]
        extra_kwargs = {
            'resume': {'required': False, 'allow_null': True},
            'cover_letter': {'required': False, 'allow_null': True},
            'job_posting_url': {'required': False, 'allow_blank': True},
            'location': {'required': False, 'allow_blank': True},
            'salary_range': {'required': False, 'allow_blank': True},
            'notes': {'required': False, 'allow_blank': True},
        }

    def validate(self, data):
        request = self.context.get('request')
        if not request:
            raise serializers.ValidationError("Request context is missing")

        user_uid = request.headers.get('X-User-UID')
        job_url = data.get('job_posting_url')

        if job_url and Application.objects.filter(user_uid=user_uid, job_posting_url=job_url).exists():
            raise serializers.ValidationError("You have already saved this job.")

        return data



    def create(self, validated_data):
        # Ensure a date is stored, not datetime
        if isinstance(validated_data.get("application_date"), timezone.datetime):
            validated_data["application_date"] = validated_data["application_date"].date()
        return super().create(validated_data)


class UpdateApplicationSerializer(serializers.ModelSerializer):
    application_date = serializers.DateField(
        required=False,
        input_formats=['%Y-%m-%d']
    )

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


# ---------------------------
# Job Serializer
# ---------------------------
class JobSerializer(serializers.ModelSerializer):
    posted_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", required=False)
    fetched_at = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%SZ", required=False)

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company', 'location',
            'salary_min', 'salary_max', 'link', 'source',
            'posted_at', 'fetched_at'
        ]


# ---------------------------
# Job Filter Serializer
# ---------------------------
class JobFilterSerializer(serializers.ModelSerializer):
    providers = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = JobFilter
        fields = [
            'id', 'user_uid', 'keywords', 'locations',
            'salary_min', 'remote_only', 'providers',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
