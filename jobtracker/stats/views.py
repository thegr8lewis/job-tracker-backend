from rest_framework import generics
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta
from .models import DashboardStats, AnalyticsData
from .serializers import DashboardStatsSerializer, AnalyticsDataSerializer
from applications.models import Application, TimelineEvent

class DashboardStatsView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = DashboardStatsSerializer

    def get_object(self):
        total_applications = Application.objects.count()
        this_month = timezone.now().replace(day=1)
        applications_this_month = Application.objects.filter(created_at__gte=this_month).count()

        interview_count = Application.objects.filter(status='interview').count()
        offer_count = Application.objects.filter(status='offer').count()

        interview_rate = (interview_count / total_applications * 100) if total_applications > 0 else 0
        offer_rate = (offer_count / total_applications * 100) if total_applications > 0 else 0

        stats, _ = DashboardStats.objects.get_or_create(pk=1)
        stats.total_applications = total_applications
        stats.applications_this_month = applications_this_month
        stats.interview_rate = round(interview_rate, 2)
        stats.offer_rate = round(offer_rate, 2)
        stats.save()

        return stats

# class AnalyticsView(generics.ListAPIView):
#     permission_classes = [AllowAny]
#     serializer_class = AnalyticsDataSerializer

#     def get_queryset(self):
#         period = self.request.query_params.get('period', '30d')

#         if period == '7d':
#             days = 7
#         elif period == '30d':
#             days = 30
#         elif period == '90d':
#             days = 90
#         else:
#             days = 30

#         start_date = timezone.now() - timedelta(days=days)

#         # Update or create AnalyticsData for each date
#         for i in range(days + 1):
#             date = (start_date + timedelta(days=i)).date()
#             applications = Application.objects.filter(created_at__date=date).count()
#             interviews = TimelineEvent.objects.filter(
#                 event_type='interview',
#                 date__date=date
#             ).count()
#             offers = TimelineEvent.objects.filter(
#                 event_type='offer',
#                 date__date=date
#             ).count()

#             AnalyticsData.objects.update_or_create(
#                 date=date,
#                 defaults={
#                     'applications_count': applications,
#                     'interviews_count': interviews,
#                     'offers_count': offers
#                 }
#             )

#         return AnalyticsData.objects.filter(date__gte=start_date).order_by('date')

class AnalyticsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = AnalyticsDataSerializer

    def get_queryset(self):
        period = self.request.query_params.get('period', '30d')

        if period == '7d':
            days = 7
        elif period == '30d':
            days = 30
        elif period == '90d':
            days = 90
        else:
            days = 30

        start_date = timezone.now() - timedelta(days=days)

        # Update or create AnalyticsData for each date
        for i in range(days + 1):
            current_date = (start_date + timedelta(days=i)).date()
            
            # Remove __date from the lookups
            applications = Application.objects.filter(created_at__date=current_date).count()
            interviews = TimelineEvent.objects.filter(
                event_type='interview',
                date=current_date  # Just use the date directly
            ).count()
            offers = TimelineEvent.objects.filter(
                event_type='offer',
                date=current_date  # Just use the date directly
            ).count()

            AnalyticsData.objects.update_or_create(
                date=current_date,
                defaults={
                    'applications_count': applications,
                    'interviews_count': interviews,
                    'offers_count': offers
                }
            )

        return AnalyticsData.objects.filter(date__gte=start_date.date()).order_by('date')