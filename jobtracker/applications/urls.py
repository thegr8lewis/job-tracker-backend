# from django.urls import path
# from .views import (
#     ApplicationListCreateView,
#     ApplicationRetrieveUpdateDestroyView,
#     UpdateApplicationStatusView,
#     AddTimelineEventView,
#     TimelineEventListView,
#     TimelineEventUpdateDeleteView,
#     JobListView,
#     JobFilterListCreateView,
#     JobFilterRetrieveUpdateDestroyView,
#     TriggerFetchNowView,
#     GmailConnectView,
#     GmailCallbackView,
#     GmailDisconnectView,
#     UserEmailSettingsView,
#     ApplicationEmailLogsView,
#     TriggerEmailProcessingView,
# )

# urlpatterns = [
#     path('', ApplicationListCreateView.as_view(), name='application-list-create'),
#     path('<int:pk>/', ApplicationRetrieveUpdateDestroyView.as_view(), name='application-retrieve-update-destroy'),
#     path('<int:pk>/status/', UpdateApplicationStatusView.as_view(), name='update-application-status'),
#     path('<int:pk>/timeline/', AddTimelineEventView.as_view(), name='add-timeline-event'),
#     path('<int:pk>/timeline/events/', TimelineEventListView.as_view(), name='list-timeline-events'),
#     path('<int:pk>/timeline/<int:event_id>/', TimelineEventUpdateDeleteView.as_view(), name='update-delete-timeline-event'),

#     # Jobs
#     path('jobs/', JobListView.as_view(), name='job-list'),

#     # Filters
#     path('filters/', JobFilterListCreateView.as_view(), name='jobfilter-list-create'),
#     path('filters/<int:pk>/', JobFilterRetrieveUpdateDestroyView.as_view(), name='jobfilter-rud'),

#     # Trigger fetch now
#     path('fetch-now/', TriggerFetchNowView.as_view(), name='fetch-now'),

#     # Email Tracking Endpoints
#     path('email/connect/', GmailConnectView.as_view(), name='gmail-connect'),
#     path('email/callback/', GmailCallbackView.as_view(), name='gmail-callback'),
#     path('email/disconnect/', GmailDisconnectView.as_view(), name='gmail-disconnect'),
#     path('email/settings/', UserEmailSettingsView.as_view(), name='email-settings'),
#     path('<int:pk>/email-logs/', ApplicationEmailLogsView.as_view(), name='application-email-logs'),
#     path('email/process/', TriggerEmailProcessingView.as_view(), name='trigger-email-processing'),
# ]



from django.urls import path
from .views import (
    ApplicationListCreateView,
    ApplicationRetrieveUpdateDestroyView,
    UpdateApplicationStatusView,
    AddTimelineEventView,
    TimelineEventListView,
    TimelineEventUpdateDeleteView,
    JobListView,
    JobFilterListCreateView,
    JobFilterRetrieveUpdateDestroyView,
    TriggerFetchNowView,
    GmailConnectView,
    GmailCallbackView,
    GmailDisconnectView,
    UserEmailSettingsView,
    ApplicationEmailLogsView,
    TriggerEmailProcessingView,
    HealthCheckView
)

urlpatterns = [
    # Application endpoints
    path('', ApplicationListCreateView.as_view(), name='application-list-create'),
    path('<int:pk>/', ApplicationRetrieveUpdateDestroyView.as_view(), name='application-retrieve-update-destroy'),
    path('<int:pk>/status/', UpdateApplicationStatusView.as_view(), name='update-application-status'),
    
    # Timeline endpoints
    path('<int:pk>/timeline/', AddTimelineEventView.as_view(), name='add-timeline-event'),
    path('<int:pk>/timeline/events/', TimelineEventListView.as_view(), name='list-timeline-events'),
    path('<int:pk>/timeline/<int:event_id>/', TimelineEventUpdateDeleteView.as_view(), name='update-delete-timeline-event'),

    # Jobs endpoints
    path('jobs/', JobListView.as_view(), name='job-list'),

    # Filters endpoints
    path('filters/', JobFilterListCreateView.as_view(), name='jobfilter-list-create'),
    path('filters/<int:pk>/', JobFilterRetrieveUpdateDestroyView.as_view(), name='jobfilter-rud'),

    # Trigger fetch now
    path('fetch-now/', TriggerFetchNowView.as_view(), name='fetch-now'),

    # Email Tracking Endpoints
    path('email/connect/', GmailConnectView.as_view(), name='gmail-connect'),
    path('email/callback/', GmailCallbackView.as_view(), name='gmail-callback'),
    path('email/disconnect/', GmailDisconnectView.as_view(), name='gmail-disconnect'),
    path('email/settings/', UserEmailSettingsView.as_view(), name='email-settings'),
    path('email/process/', TriggerEmailProcessingView.as_view(), name='trigger-email-processing'),
    
    # Email logs endpoint (make sure this is included)
    path('<int:pk>/email-logs/', ApplicationEmailLogsView.as_view(), name='application-email-logs'),
    path("health/", HealthCheckView.as_view(), name="health"),
]