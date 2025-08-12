from django.urls import path
from .views import (
    ApplicationListCreateView,
    ApplicationRetrieveUpdateDestroyView,
    UpdateApplicationStatusView,
    AddTimelineEventView,
    TimelineEventListView,
    TimelineEventUpdateDeleteView
)

urlpatterns = [
    path('', ApplicationListCreateView.as_view(), name='application-list-create'),
    path('<int:pk>/', ApplicationRetrieveUpdateDestroyView.as_view(), name='application-retrieve-update-destroy'),
    path('<int:pk>/status/', UpdateApplicationStatusView.as_view(), name='update-application-status'),
    path('<int:pk>/timeline/', AddTimelineEventView.as_view(), name='add-timeline-event'),
    path('<int:pk>/timeline/events/', TimelineEventListView.as_view(), name='list-timeline-events'),
    path('<int:pk>/timeline/<int:event_id>/', TimelineEventUpdateDeleteView.as_view(), name='update-delete-timeline-event'),
]