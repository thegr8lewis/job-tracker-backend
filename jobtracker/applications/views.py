# from rest_framework import generics, status
# from rest_framework.response import Response
# from django.shortcuts import get_object_or_404
# from django.utils import timezone
# from .services.job_fetcher import JobFetcherService

# from .models import Application, TimelineEvent, Job, JobFilter
# from .serializers import (
#     ApplicationSerializer,
#     CreateApplicationSerializer,
#     UpdateApplicationSerializer,
#     UpdateStatusSerializer,
#     AddTimelineEventSerializer,
#     TimelineEventSerializer,
#     JobSerializer,
#     JobFilterSerializer
# )

# from .tasks import fetch_jobs_daily


# class ApplicationListCreateView(generics.ListCreateAPIView):
#     serializer_class = ApplicationSerializer
#     def get_queryset(self):
#         user_uid = self.request.headers.get('X-User-UID')
#         qs = Application.objects.filter(user_uid=user_uid).order_by('-created_at')
#         status_param = self.request.query_params.get("status")
#         if status_param:
#             qs = qs.filter(status=status_param)
#         return qs
#     def perform_create(self, serializer):
#         user_uid = self.request.headers.get('X-User-UID')
#         serializer.save(user_uid=user_uid)


# class ApplicationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Application.objects.all()
#     def get_serializer_class(self):
#         return UpdateApplicationSerializer if self.request.method in ('PUT','PATCH') else ApplicationSerializer


# class UpdateApplicationStatusView(generics.UpdateAPIView):
#     queryset = Application.objects.all()
#     serializer_class = UpdateStatusSerializer
#     def update(self, request, *args, **kwargs):
#         instance = self.get_object()
#         serializer = self.get_serializer(instance, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         instance.status = serializer.validated_data['status']
#         instance.save()
#         TimelineEvent.objects.create(
#             application=instance,
#             event_type='status_change',
#             title=f'Status changed to {instance.status}',
#             description=f'Application status updated to {instance.status}',
#             completed=True
#         )
#         return Response(ApplicationSerializer(instance).data)


# class AddTimelineEventView(generics.CreateAPIView):
#     serializer_class = AddTimelineEventSerializer
#     def create(self, request, *args, **kwargs):
#         application = get_object_or_404(Application, pk=self.kwargs['pk'])
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         event = TimelineEvent.objects.create(
#             application=application,
#             event_type=serializer.validated_data['event_type'],
#             title=serializer.validated_data['title'],
#             description=serializer.validated_data.get('description', ''),
#             date=serializer.validated_data.get('date', timezone.now().date()),
#             completed=serializer.validated_data.get('completed', False)
#         )
#         return Response(TimelineEventSerializer(event).data, status=status.HTTP_201_CREATED)


# class TimelineEventListView(generics.ListAPIView):
#     serializer_class = TimelineEventSerializer
#     def get_queryset(self):
#         return TimelineEvent.objects.filter(application_id=self.kwargs['pk']).order_by('-date')


# class TimelineEventUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = TimelineEvent.objects.all()
#     serializer_class = AddTimelineEventSerializer
#     def get_object(self):
#         app_id = self.kwargs['pk']
#         event_id = self.kwargs['event_id']
#         return get_object_or_404(TimelineEvent, application_id=app_id, id=event_id)


# # ✅ Job endpoints
# class JobListView(generics.ListAPIView):
#     serializer_class = JobSerializer

#     def list(self, request, *args, **kwargs):
#         q_kw = request.query_params.get('q', '')
#         q_loc = request.query_params.get('loc', '')

#         # Fetch live jobs from providers
#         service = JobFetcherService()
#         jobs = service.fetch_all(q_kw, q_loc, providers=["jooble"])

#         return Response(jobs)

# # ✅ JobFilter endpoints
# class JobFilterListCreateView(generics.ListCreateAPIView):
#     serializer_class = JobFilterSerializer
#     def get_queryset(self):
#         user_uid = self.request.headers.get('X-User-UID')
#         return JobFilter.objects.filter(user_uid=user_uid).order_by('-updated_at')
#     def perform_create(self, serializer):
#         user_uid = self.request.headers.get('X-User-UID')
#         serializer.save(user_uid=user_uid)


# class JobFilterRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = JobFilter.objects.all()
#     serializer_class = JobFilterSerializer


# # ✅ Trigger fetch now (optional; Celery beat will do this daily)
# class TriggerFetchNowView(generics.GenericAPIView):
#     def post(self, request, *args, **kwargs):
#         result = fetch_jobs_daily()
#         return Response({"detail": "Fetch started", "result": result})




from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from rest_framework import serializers


from .services.job_fetcher import JobFetcherService
from .email_services import GmailService
from .tasks import fetch_jobs_daily, process_user_emails

from .models import Application, TimelineEvent, Job, JobFilter, UserEmailSettings, EmailLog
from .serializers import (
    ApplicationSerializer,
    CreateApplicationSerializer,
    UpdateApplicationSerializer,
    UpdateStatusSerializer,
    AddTimelineEventSerializer,
    TimelineEventSerializer,
    JobSerializer,
    JobFilterSerializer,
    UserEmailSettingsSerializer,
    EmailLogSerializer
)

class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer
    def get_queryset(self):
        user_uid = self.request.headers.get('X-User-UID')
        qs = Application.objects.filter(user_uid=user_uid).order_by('-created_at')
        status_param = self.request.query_params.get("status")
        if status_param:
            qs = qs.filter(status=status_param)
        return qs
    def perform_create(self, serializer):
        user_uid = self.request.headers.get('X-User-UID')
        serializer.save(user_uid=user_uid)

class ApplicationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()
    def get_serializer_class(self):
        return UpdateApplicationSerializer if self.request.method in ('PUT','PATCH') else ApplicationSerializer

class UpdateApplicationStatusView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = UpdateStatusSerializer
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        instance.status = serializer.validated_data['status']
        instance.save()
        TimelineEvent.objects.create(
            application=instance,
            event_type='status_change',
            title=f'Status changed to {instance.status}',
            description=f'Application status updated to {instance.status}',
            completed=True
        )
        return Response(ApplicationSerializer(instance).data)

class AddTimelineEventView(generics.CreateAPIView):
    serializer_class = AddTimelineEventSerializer
    def create(self, request, *args, **kwargs):
        application = get_object_or_404(Application, pk=self.kwargs['pk'])
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = TimelineEvent.objects.create(
            application=application,
            event_type=serializer.validated_data['event_type'],
            title=serializer.validated_data['title'],
            description=serializer.validated_data.get('description', ''),
            date=serializer.validated_data.get('date', timezone.now().date()),
            completed=serializer.validated_data.get('completed', False)
        )
        return Response(TimelineEventSerializer(event).data, status=status.HTTP_201_CREATED)

class TimelineEventListView(generics.ListAPIView):
    serializer_class = TimelineEventSerializer
    def get_queryset(self):
        return TimelineEvent.objects.filter(application_id=self.kwargs['pk']).order_by('-date')

class TimelineEventUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimelineEvent.objects.all()
    serializer_class = AddTimelineEventSerializer
    def get_object(self):
        app_id = self.kwargs['pk']
        event_id = self.kwargs['event_id']
        return get_object_or_404(TimelineEvent, application_id=app_id, id=event_id)

# ✅ Job endpoints
class JobListView(generics.ListAPIView):
    serializer_class = JobSerializer

    def list(self, request, *args, **kwargs):
        q_kw = request.query_params.get('q', '')
        q_loc = request.query_params.get('loc', '')

        # Fetch live jobs from providers
        service = JobFetcherService()
        jobs = service.fetch_all(q_kw, q_loc, providers=["jooble"])

        return Response(jobs)

# ✅ JobFilter endpoints
class JobFilterListCreateView(generics.ListCreateAPIView):
    serializer_class = JobFilterSerializer
    def get_queryset(self):
        user_uid = self.request.headers.get('X-User-UID')
        return JobFilter.objects.filter(user_uid=user_uid).order_by('-updated_at')
    def perform_create(self, serializer):
        user_uid = self.request.headers.get('X-User-UID')
        serializer.save(user_uid=user_uid)

class JobFilterRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobFilter.objects.all()
    serializer_class = JobFilterSerializer

# ✅ Trigger fetch now (optional; Celery beat will do this daily)
class TriggerFetchNowView(generics.GenericAPIView):
    def post(self, request, *args, **kwargs):
        result = fetch_jobs_daily()
        return Response({"detail": "Fetch started", "result": result})

# ✅ Email Tracking Endpoints
class GmailConnectView(APIView):
    def get(self, request):
        user_uid = request.headers.get('X-User-UID')
        if not user_uid:
            return Response({"error": "X-User-UID header required"}, status=status.HTTP_400_BAD_REQUEST)
        
        gmail_service = GmailService()
        auth_url = gmail_service.get_oauth_url(user_uid)
        
        return Response({"auth_url": auth_url})

class GmailCallbackView(APIView):
    def get(self, request):
        code = request.GET.get('code')
        state = request.GET.get('state')
        
        if not code or not state:
            return Response({"error": "Missing code or state"}, status=status.HTTP_400_BAD_REQUEST)
        
        gmail_service = GmailService()
        success = gmail_service.handle_oauth_callback(code, state)
        
        if success:
            return Response({"success": "Gmail connected successfully"})
        else:
            return Response({"error": "Failed to connect Gmail"}, status=status.HTTP_400_BAD_REQUEST)

class GmailDisconnectView(APIView):
    def post(self, request):
        user_uid = request.headers.get('X-User-UID')
        if not user_uid:
            return Response({"error": "X-User-UID header required"}, status=status.HTTP_400_BAD_REQUEST)
        
        gmail_service = GmailService()
        success = gmail_service.disconnect_gmail(user_uid)
        
        if success:
            return Response({"success": "Gmail disconnected successfully"})
        else:
            return Response({"error": "Failed to disconnect Gmail"}, status=status.HTTP_400_BAD_REQUEST)

class UserEmailSettingsView(generics.RetrieveUpdateAPIView):
    serializer_class = UserEmailSettingsSerializer
    
    def get_object(self):
        user_uid = self.request.headers.get('X-User-UID')
        if not user_uid:
            raise generics.ValidationError("X-User-UID header required")
        
        settings_obj, created = UserEmailSettings.objects.get_or_create(
            user_uid=user_uid,
            defaults={'email_tracking_enabled': True}
        )
        return settings_obj


# class ApplicationEmailLogsView(generics.ListAPIView):
#     serializer_class = EmailLogSerializer
    
#     def get_queryset(self):
#         application_id = self.kwargs['pk']
#         user_uid = self.request.headers.get('X-User-UID')
        
#         print(f"DEBUG: Fetching email logs for application ID: {application_id}")
#         print(f"DEBUG: User UID from header: {user_uid}")
        
#         if not user_uid:
#             print("DEBUG: No X-User-UID header provided")
#             raise generics.ValidationError("X-User-UID header required")
        
#         # Check if any application exists with this ID
#         application_exists = Application.objects.filter(id=application_id).exists()
#         print(f"DEBUG: Application with ID {application_id} exists: {application_exists}")
        
#         if application_exists:
#             # Check if user owns this application
#             user_owns_application = Application.objects.filter(
#                 id=application_id, 
#                 user_uid=user_uid
#             ).exists()
#             print(f"DEBUG: User owns application: {user_owns_application}")
        
#         # Verify user owns this application
#         application = get_object_or_404(Application, id=application_id, user_uid=user_uid)
        
#         email_logs = EmailLog.objects.filter(application=application).order_by('-processed_at')
#         print(f"DEBUG: Found {email_logs.count()} email logs")
        
#         return email_logs

class ApplicationEmailLogsView(generics.ListAPIView):
    serializer_class = EmailLogSerializer
    
    def get_queryset(self):
        application_id = self.kwargs['pk']
        user_uid = self.request.headers.get('X-User-UID')

        # ✅ Fallback to authenticated user if header missing
        if not user_uid and self.request.user and self.request.user.is_authenticated:
            user_uid = str(self.request.user.id)  # adjust if you store UID differently

        if not user_uid:
            # Graceful error (400) instead of server error (500)
            raise serializers.ValidationError(
                {"error": "User identifier required (X-User-UID header or authenticated user)"}
            )

        print(f"DEBUG: Fetching email logs for application ID: {application_id}")
        print(f"DEBUG: Using User UID: {user_uid}")

        # Verify application exists and belongs to user
        application = get_object_or_404(Application, id=application_id, user_uid=user_uid)
        
        email_logs = EmailLog.objects.filter(application=application).order_by('-processed_at')
        print(f"DEBUG: Found {email_logs.count()} email logs")

        return email_logs



class TriggerEmailProcessingView(APIView):
    def post(self, request):
        user_uid = request.headers.get('X-User-UID')
        if not user_uid:
            return Response({"error": "X-User-UID header required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Process emails asynchronously
        process_user_emails.delay(user_uid)
        
        return Response({"success": "Email processing started"})