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
#     user_uid = models.CharField(max_length=255, default="unknown")
#     company_name = models.CharField(max_length=255)
#     job_title = models.CharField(max_length=255)
#     job_posting_url = models.URLField(max_length=500, blank=True, null=True)
#     location = models.CharField(max_length=255, blank=True, null=True)
#     salary_range = models.CharField(max_length=255, blank=True, null=True)
#     application_date = models.DateField(default=timezone.localdate)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
#     notes = models.TextField(blank=True, null=True)
#     resume = models.FileField(upload_to='resumes/', blank=True, null=True)
#     cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=["user_uid", "job_posting_url"],
#                 name="unique_user_application"
#             )
#         ]

#     def __str__(self):
#         return f"{self.job_title} at {self.company_name}"


# class TimelineEvent(models.Model):
#     application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='timeline_events')
#     event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     date = models.DateField(default=timezone.localdate)  # FIXED
#     completed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.event_type} - {self.title}"

#     class Meta:
#         ordering = ['-date']


# class Job(models.Model):
#     title = models.CharField(max_length=255)
#     company = models.CharField(max_length=255, blank=True, null=True)
#     location = models.CharField(max_length=255, blank=True, null=True)
#     salary_min = models.IntegerField(blank=True, null=True)
#     salary_max = models.IntegerField(blank=True, null=True)
#     link = models.URLField(unique=True)
#     source = models.CharField(max_length=50, blank=True, null=True)  # jooble, adzuna, workable, rapidapi-*
#     posted_at = models.DateTimeField(blank=True, null=True)           # provider’s “created” date/time
#     fetched_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.title} at {self.company or 'Unknown'}"


# class JobFilter(models.Model):
#     user_uid = models.CharField(max_length=255)
#     keywords = models.JSONField(default=list)
#     locations = models.JSONField(default=list)
#     salary_min = models.IntegerField(blank=True, null=True)
#     remote_only = models.BooleanField(default=False)
#     providers = models.JSONField(default=list)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Filter for {self.user_uid} ({', '.join(self.keywords)})"


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
    ('email_received', 'Email Received'),  # New event type
]

# New choices for email classification
EMAIL_CLASSIFICATION_CHOICES = [
    ('REJECTION', 'Rejection'),
    ('INTERVIEW', 'Interview'),
    ('OFFER', 'Offer'),
    ('FOLLOW_UP', 'Follow Up'),
    ('APPLICATION_RECEIVED', 'Application Received'),
    ('OTHER', 'Other'),
]

class Application(models.Model):
    user_uid = models.CharField(max_length=255, default="unknown")
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    job_posting_url = models.URLField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    salary_range = models.CharField(max_length=255, blank=True, null=True)
    application_date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
    notes = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
    applied_date = models.DateField(null=True, blank=True)
    
    # New fields for email tracking
    email_tracking_enabled = models.BooleanField(default=False)
    company_email_domains = models.JSONField(default=list, blank=True)  # e.g., ["google.com", "hr.google.com"]
    last_email_check = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_uid", "job_posting_url"],
                name="unique_user_application"
            )
        ]

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class TimelineEvent(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='timeline_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.localdate)
    completed = models.BooleanField(default=False)
    
    # New fields for email-generated events
    is_auto_generated = models.BooleanField(default=False)
    email_log = models.ForeignKey('EmailLog', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.title}"

    class Meta:
        ordering = ['-date']

# New model for user email settings
# class UserEmailSettings(models.Model):
#     user_uid = models.CharField(max_length=255, unique=True)
#     gmail_connected = models.BooleanField(default=False)
#     gmail_refresh_token = models.TextField(blank=True, null=True)
#     gmail_access_token = models.TextField(blank=True, null=True)
#     gmail_token_expires_at = models.DateTimeField(null=True, blank=True)
#     email_tracking_enabled = models.BooleanField(default=False)
#     auto_process_emails = models.BooleanField(default=False)
    
    
#     # Email processing preferences
#     auto_update_enabled = models.BooleanField(default=True)
#     confidence_threshold = models.IntegerField(default=80)  # Only auto-update if AI is >80% confident
#     notification_enabled = models.BooleanField(default=True)
    
#     last_email_sync = models.DateTimeField(null=True, blank=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Email settings for {self.user_uid}"


class UserEmailSettings(models.Model):
    user_uid = models.CharField(max_length=255, unique=True)
    gmail_connected = models.BooleanField(default=False)
    gmail_refresh_token = models.TextField(blank=True, null=True)
    gmail_access_token = models.TextField(blank=True, null=True)
    gmail_token_expires_at = models.DateTimeField(null=True, blank=True)
    email_tracking_enabled = models.BooleanField(default=False)
    auto_process_emails = models.BooleanField(default=False)
   


    # Email processing preferences
    auto_update_enabled = models.BooleanField(default=True)
    confidence_threshold = models.IntegerField(default=80)
    notification_enabled = models.BooleanField(default=True)
    
    last_email_sync = models.DateTimeField(null=True, blank=True)
    last_email_check = models.DateTimeField(null=True, blank=True)  # <-- add this
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# New model for email logs
class EmailLog(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='email_logs')
    user_uid = models.CharField(max_length=255)
    
    # Email metadata
    email_id = models.CharField(max_length=255, unique=True)  # Gmail message ID
    thread_id = models.CharField(max_length=255, blank=True, null=True)
    sender_email = models.EmailField()
    sender_name = models.CharField(max_length=255, blank=True, null=True)
    subject = models.CharField(max_length=500)
    snippet = models.TextField(blank=True, null=True)  # Email preview
    received_date = models.DateTimeField()
    
    # AI Analysis results
    classification = models.CharField(max_length=20, choices=EMAIL_CLASSIFICATION_CHOICES, blank=True, null=True)
    confidence_score = models.IntegerField(null=True, blank=True)  # 0-100
    ai_analysis = models.JSONField(default=dict, blank=True)  # Full AI response
    suggested_status = models.CharField(max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    
    # Processing status
    processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    status_updated = models.BooleanField(default=False)
    timeline_created = models.BooleanField(default=False)
    user_reviewed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Email from {self.sender_email} - {self.subject[:50]}"

    class Meta:
        ordering = ['-received_date']

class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    salary_min = models.IntegerField(blank=True, null=True)
    salary_max = models.IntegerField(blank=True, null=True)
    link = models.URLField(unique=True)
    source = models.CharField(max_length=50, blank=True, null=True)  # jooble, adzuna, workable, rapidapi-*
    posted_at = models.DateTimeField(blank=True, null=True)           # provider's "created" date/time
    fetched_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} at {self.company or 'Unknown'}"

class JobFilter(models.Model):
    user_uid = models.CharField(max_length=255)
    keywords = models.JSONField(default=list)
    locations = models.JSONField(default=list)
    salary_min = models.IntegerField(blank=True, null=True)
    remote_only = models.BooleanField(default=False)
    providers = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Filter for {self.user_uid} ({', '.join(self.keywords)})"