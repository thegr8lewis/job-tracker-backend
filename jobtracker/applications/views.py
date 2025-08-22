from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Application, TimelineEvent
from .serializers import (
    ApplicationSerializer,
    CreateApplicationSerializer,
    UpdateApplicationSerializer,
    UpdateStatusSerializer,
    AddTimelineEventSerializer,
    TimelineEventSerializer
)
import traceback
from django.utils import timezone

class ApplicationListCreateView(generics.ListCreateAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        user_uid = self.request.headers.get('X-User-UID')
        return Application.objects.filter(user_uid=user_uid).order_by('-created_at')

    def perform_create(self, serializer):
        user_uid = self.request.headers.get('X-User-UID')
        serializer.save(user_uid=user_uid)


class ApplicationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Application.objects.all()

    def get_serializer_class(self):
        return UpdateApplicationSerializer if self.request.method == 'PUT' else ApplicationSerializer

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
        try:
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
            
        except Exception as e:
            traceback.print_exc()
            return Response(
                {'error': str(e), 'details': traceback.format_exc()},
                status=status.HTTP_400_BAD_REQUEST
            )

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