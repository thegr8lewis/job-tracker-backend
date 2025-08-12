from rest_framework import serializers
from .models import DashboardStats, AnalyticsData

class DashboardStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DashboardStats
        fields = '__all__'

class AnalyticsDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnalyticsData
        fields = '__all__'
