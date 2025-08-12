# models.py - Add these fields to your Application model

from django.db import models

from django.core.files.storage import FileSystemStorage

class UserFileStorage(FileSystemStorage):
    pass


class Application(models.Model):
    # Your existing fields...
    company_name = models.CharField(max_length=255)
    job_title = models.CharField(max_length=255)
    job_posting_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    salary_range = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=50, default='applied')
    notes = models.TextField(blank=True, null=True)
    application_date = models.DateField()
    
    # ADD THESE FIELDS to store resume and cover letter URLs
    resume_url = models.URLField(blank=True, null=True)
    cover_letter_url = models.URLField(blank=True, null=True)
    resume_content = models.TextField(blank=True, null=True)  # For extracted text content
    cover_letter_content = models.TextField(blank=True, null=True)  # For extracted text content
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

class Resume(models.Model):
    file = models.FileField(upload_to='resumes/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255)

    def __str__(self):
        return self.original_filename

class CoverLetter(models.Model):
    file = models.FileField(upload_to='cover_letters/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    original_filename = models.CharField(max_length=255)

    def __str__(self):
        return self.original_filename