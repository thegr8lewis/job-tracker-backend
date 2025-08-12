from django.urls import path
from .views import UploadResumeView, UploadCoverLetterView

urlpatterns = [
    path('resume/', UploadResumeView.as_view(), name='upload-resume'),
    path('cover-letter/', UploadCoverLetterView.as_view(), name='upload-cover-letter'),

]