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
#     application_date = models.DateField(default=timezone.now)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
#     notes = models.TextField(blank=True, null=True)
#     resume = models.FileField(upload_to='resumes/', blank=True, null=True)
#     cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.job_title} at {self.company_name}"


# class TimelineEvent(models.Model):
#     application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='timeline_events')
#     event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
#     title = models.CharField(max_length=255)
#     description = models.TextField(blank=True, null=True)
#     date = models.DateField(default=timezone.now)
#     completed = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.event_type} - {self.title}"

#     class Meta:
#         ordering = ['-date']


# # ✅ Expanded Job model to support multiple APIs
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


# # ✅ New per-user saved filters for daily fetching
# class JobFilter(models.Model):
#     user_uid = models.CharField(max_length=255)
#     keywords = models.JSONField(default=list)     # ["React Developer", "Frontend Engineer"]
#     locations = models.JSONField(default=list)    # ["Nairobi", "Remote"]
#     salary_min = models.IntegerField(blank=True, null=True)
#     remote_only = models.BooleanField(default=False)
#     providers = models.JSONField(default=list)    # e.g. ["jooble","adzuna"] (optional; empty = all)
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


# class Application(models.Model):
#     user_uid = models.CharField(max_length=255, default="unknown")
#     company_name = models.CharField(max_length=255)
#     job_title = models.CharField(max_length=255)
#     job_posting_url = models.URLField(max_length=500, blank=True, null=True)
#     location = models.CharField(max_length=255, blank=True, null=True)
#     salary_range = models.CharField(max_length=255, blank=True, null=True)
#     application_date = models.DateField(default=timezone.localdate)  # FIXED
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='applied')
#     notes = models.TextField(blank=True, null=True)
#     resume = models.FileField(upload_to='resumes/', blank=True, null=True)
#     cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.job_title} at {self.company_name}"


class TimelineEvent(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='timeline_events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(default=timezone.localdate)  # FIXED
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_type} - {self.title}"

    class Meta:
        ordering = ['-date']


class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    salary_min = models.IntegerField(blank=True, null=True)
    salary_max = models.IntegerField(blank=True, null=True)
    link = models.URLField(unique=True)
    source = models.CharField(max_length=50, blank=True, null=True)  # jooble, adzuna, workable, rapidapi-*
    posted_at = models.DateTimeField(blank=True, null=True)           # provider’s “created” date/time
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
