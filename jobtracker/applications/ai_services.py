# import os
# import logging
# import json
# import re
# from typing import Dict, Optional
# import google.generativeai as genai
# from django.conf import settings

# logger = logging.getLogger('applications.ai_services')

# class GeminiEmailAnalyzer:
#     """
#     Service for analyzing job-related emails using Google Gemini Flash 1.5
#     """
    
#     def __init__(self):
#         api_key = settings.GOOGLE_GEMINI_API_KEY
#         if not api_key:
#             raise ValueError("GOOGLE_GEMINI_API_KEY not configured")
        
#         genai.configure(api_key=api_key)
#         self.model = genai.GenerativeModel('gemini-1.5-flash')
    
#     def analyze_job_email(self, email_data: Dict, application_data: Dict) -> Optional[Dict]:
#         """
#         Analyze a job-related email using Gemini AI
#         Returns structured analysis including classification, confidence, and notes
#         """
#         try:
#             prompt = self._build_prompt(email_data, application_data)
            
#             response = self.model.generate_content(prompt)
            
#             if not response.text:
#                 logger.error("Empty response from Gemini")
#                 return None
            
#             # Extract JSON from response
#             json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
#             if not json_match:
#                 logger.error(f"No JSON found in Gemini response: {response.text}")
#                 return None
            
#             analysis = json.loads(json_match.group())
            
#             # Validate required fields
#             required_fields = ['classification', 'confidence', 'timeline_note']
#             if not all(field in analysis for field in required_fields):
#                 logger.error(f"Missing required fields in analysis: {analysis}")
#                 return None
            
#             return analysis
            
#         except Exception as e:
#             logger.error(f"Error analyzing email with Gemini: {str(e)}")
#             return None
    
#     def _build_prompt(self, email_data: Dict, application_data: Dict) -> str:
#         """Build the prompt for Gemini analysis"""
#         return f"""
# Analyze this job application email and determine:

# Job Application: {application_data.get('job_title', 'Unknown')} at {application_data.get('company_name', 'Unknown Company')}
# Applied Date: {application_data.get('application_date', 'Unknown')}
# Current Status: {application_data.get('status', 'Unknown')}

# Email Details:
# From: {email_data.get('sender_email', 'Unknown')}
# Subject: {email_data.get('subject', 'No Subject')}
# Body Preview: {email_data.get('body', '')[:1000]}{'...' if len(email_data.get('body', '')) > 1000 else ''}

# Tasks:
# 1. Classify email intent: [REJECTION, INTERVIEW, OFFER, FOLLOWUP, SCREENING, ASSESSMENT, OTHER]
# 2. Confidence score (0-100)
# 3. Generate timeline note (max 100 chars)
# 4. Suggest new status if applicable (keep current if no change needed)
# 5. Extract key details (interview time, next steps, etc.)

# Response format MUST be valid JSON:
# {{
#   "classification": "INTERVIEW",
#   "confidence": 95,
#   "timeline_note": "Interview invitation received for Software Engineer position",
#   "suggested_status": "INTERVIEW_SCHEDULED",
#   "key_details": "Interview scheduled for next Tuesday at 2 PM"
# }}

# Only respond with the JSON object, no additional text.
# """
    
#     def classify_status_change(self, classification: str, confidence: int) -> Optional[str]:
#         """
#         Map email classification to application status with confidence threshold
#         """
#         if confidence < 80:  # Minimum confidence threshold
#             return None
        
#         status_mapping = {
#             'REJECTION': 'rejected',
#             'INTERVIEW': 'interview',
#             'SCREENING': 'interview',
#             'ASSESSMENT': 'interview',
#             'OFFER': 'offer',
#             'FOLLOWUP': None,  # No status change for follow-ups
#             'OTHER': None
#         }
        
#         return status_mapping.get(classification.upper())



import os
import logging
import json
import re
from typing import Dict, Optional
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger('applications.ai_services')

class GeminiEmailAnalyzer:
    """
    Service for analyzing job-related emails using Google Gemini Flash 1.5
    """

    def __init__(self):
        api_key = settings.GOOGLE_GEMINI_API_KEY
        if not api_key:
            raise ValueError("GOOGLE_GEMINI_API_KEY not configured")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def analyze_job_email(self, email_data: Dict, application_data: Dict) -> Optional[Dict]:
        """
        Analyze a job-related email using Gemini AI
        Returns structured analysis including classification, confidence, and notes
        """
        try:
            prompt = self._build_prompt(email_data, application_data)

            response = self.model.generate_content(prompt)

            if not response.text:
                logger.error("Empty response from Gemini")
                return None

            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if not json_match:
                logger.error(f"No JSON found in Gemini response: {response.text}")
                return None

            analysis = json.loads(json_match.group())

            # Validate required fields
            required_fields = ['classification', 'confidence', 'timeline_note']
            if not all(field in analysis for field in required_fields):
                logger.error(f"Missing required fields in analysis: {analysis}")
                return None

            # Ensure classification is properly capitalized and limited to allowed options
            classification = analysis.get('classification', '').capitalize()
            if classification not in ['Interview', 'Offer', 'Rejection']:
                classification = 'Other'  # fallback if Gemini returned something else
            analysis['classification'] = classification

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing email with Gemini: {str(e)}")
            return None

    def _build_prompt(self, email_data: Dict, application_data: Dict) -> str:
        """Build the prompt for Gemini analysis"""
        return f"""
Analyze this job application email and determine:

Job Application: {application_data.get('job_title', 'Unknown')} at {application_data.get('company_name', 'Unknown Company')}
Applied Date: {application_data.get('application_date', 'Unknown')}
Current Status: {application_data.get('status', 'Unknown')}

Email Details:
From: {email_data.get('sender_email', 'Unknown')}
Subject: {email_data.get('subject', 'No Subject')}
Body Preview: {email_data.get('body', '')[:1000]}{'...' if len(email_data.get('body', '')) > 1000 else ''}

Tasks:
1. Classify email intent into ONLY one of the following: Interview, Offer, Rejection
2. Confidence score (0-100)
3. Generate timeline note (max 100 chars)
4. Suggest new status if applicable (keep current if no change needed)
5. Extract key details (interview time, next steps, etc.)

Response format MUST be valid JSON:
{{
  "classification": "Interview",
  "confidence": 95,
  "timeline_note": "Interview invitation received for Software Engineer position",
  "suggested_status": "Interview",
  "key_details": "Interview scheduled for next Tuesday at 2 PM"
}}

Only respond with the JSON object, no additional text.
"""

    def classify_status_change(self, classification: str, confidence: int) -> Optional[str]:
        """
        Map AI classification to application status with confidence threshold
        """
        if confidence < 80:  # Minimum confidence threshold
            return None

        status_mapping = {
            'Interview': 'interview',
            'Offer': 'offer',
            'Rejection': 'rejected'
        }

        return status_mapping.get(classification)
