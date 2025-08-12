from django.db import models

class DashboardStats(models.Model):
    total_applications = models.IntegerField(default=0)
    applications_this_month = models.IntegerField(default=0)
    interview_rate = models.FloatField(default=0)
    offer_rate = models.FloatField(default=0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Dashboard Stats'

class AnalyticsData(models.Model):
    date = models.DateField()
    applications_count = models.IntegerField(default=0)
    interviews_count = models.IntegerField(default=0)
    offers_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['date']
        verbose_name_plural = 'Analytics Data'
