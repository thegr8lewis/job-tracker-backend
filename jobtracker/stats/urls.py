from django.urls import path
from .views import DashboardStatsView, AnalyticsView

urlpatterns = [
    path('dashboard/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
]
