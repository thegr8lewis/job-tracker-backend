# from django.db import models
# from django.utils import timezone

# STATUS_CHOICES = [
#     ('saved', 'Saved'),
#     ('applied', 'Applied'),
#     ('interview', 'Interview'),
#     ('offer', 'Offer'),
#     ('rejected', 'Rejected'),
#     ('withdrawn', 'Withdrawn'),
# ]

# EVENT_TYPE_CHOICES = [
#     ('applied', 'Applied'),
#     ('interview', 'Interview'),
#     ('offer', 'Offer'),
#     ('rejected', 'Rejected'),
#     ('note', 'Note'),
#     ('other', 'Other'),
#     ('status_change', 'Status Change'),
# ]

# class Application(models.Model):
#     company_name = models.CharField(max_length=255)
#     job_title = models.CharField(max_length=255)
#     job_posting_url = models.URLField(max_length=500, blank=True, null=True)
#     location = models.CharField(max_length=255, blank=True, null=True)
#     salary_range = models.CharField(max_length=255, blank=True, null=True)
#     application_date = models.DateField(default=timezone.now)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
#     notes = models.TextField(blank=True, null=True)
#     resume = models.FileField(upload_to='resumes/', blank=True, null=True)
#     cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.job_title} at {self.company_name}"

#     def get_timeline_events(self):
#         return self.timeline_events.all().order_by('-date')

# class TimelineEvent(models.Model):
#     application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='timeline_events')
#     event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     date = models.DateField(default=timezone.now)  # Changed to DateField
#     completed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.event_type} - {self.title}"

#     class Meta:
#         ordering = ['-date']




from django.db import models
from django.utils import timezone

STATUS_CHOICES = [
    ('saved', 'Saved'),
    ('applied', 'Applied'),
    ('interview', 'Interview'),
    ('offer', 'Offer'),
    ('rejected', 'Rejected'),
    ('withdrawn', 'Withdrawn'),
]

EVENT_TYPE_CHOICES = [
    ('applied', 'Applied'),
    ('interview', 'Interview'),
    ('offer', 'Offer'),
    ('rejected', 'Rejected'),
    ('note', 'Note'),
    ('other', 'Other'),
    ('status_change', 'Status Change'),
]

class Application(models.Model):
    user_uid = models.CharField(max_length=255, default="unknown")
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    job_posting_url = models.URLField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    salary_range = models.CharField(max_length=255, blank=True, null=True)
    application_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    notes = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"


class TimelineEvent(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='timeline_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.now)  # Changed to DateField
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.title}"

    class Meta:
        ordering = ['-date']