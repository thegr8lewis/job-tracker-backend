# import os
# import logging
# import base64
# from datetime import datetime, timedelta, timezone
# from typing import List, Dict, Optional
# from google.auth.transport.requests import Request
# from google.oauth2.credentials import Credentials
# from google_auth_oauthlib.flow import Flow
# from googleapiclient.discovery import build
# from django.conf import settings
# from bs4 import BeautifulSoup
# from fuzzywuzzy import fuzz

# from .models import UserEmailSettings, Application, EmailLog

# logger = logging.getLogger('applications.email_services')


# class GmailService:
#     SCOPES = [
#         "https://www.googleapis.com/auth/gmail.readonly",
#         "https://www.googleapis.com/auth/userinfo.email",
#         "https://www.googleapis.com/auth/userinfo.profile",
#         "openid",
#     ]

#     def __init__(self):
#         self.client_id = settings.GOOGLE_CLIENT_ID
#         self.client_secret = settings.GOOGLE_CLIENT_SECRET
#         self.redirect_uri = settings.GOOGLE_REDIRECT_URI

#     # ----------------------
#     # OAuth Methods
#     # ----------------------
#     def get_oauth_url(self, user_uid: str) -> str:
#         flow = Flow.from_client_config(
#             {
#                 "web": {
#                     "client_id": self.client_id,
#                     "client_secret": self.client_secret,
#                     "redirect_uris": [self.redirect_uri],
#                     "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                     "token_uri": "https://oauth2.googleapis.com/token",
#                 }
#             },
#             scopes=self.SCOPES,
#             redirect_uri=self.redirect_uri
#         )
#         auth_url, _ = flow.authorization_url(
#             access_type='offline',
#             include_granted_scopes='true',
#             prompt='consent',
#             state=user_uid
#         )
#         return auth_url

#     def handle_oauth_callback(self, code: str, state: str) -> bool:
#         try:
#             user_uid = state
#             flow = Flow.from_client_config(
#                 {
#                     "web": {
#                         "client_id": self.client_id,
#                         "client_secret": self.client_secret,
#                         "redirect_uris": [self.redirect_uri],
#                         "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#                         "token_uri": "https://oauth2.googleapis.com/token",
#                     }
#                 },
#                 scopes=self.SCOPES,
#                 redirect_uri=self.redirect_uri
#             )
#             flow.fetch_token(code=code)
#             credentials = flow.credentials

#             email_settings, created = UserEmailSettings.objects.get_or_create(
#                 user_uid=user_uid,
#                 defaults={
#                     'gmail_connected': True,
#                     'gmail_refresh_token': credentials.refresh_token,
#                     'gmail_access_token': credentials.token,
#                     'gmail_token_expires_at': credentials.expiry,
#                 }
#             )
#             if not created:
#                 email_settings.gmail_connected = True
#                 email_settings.gmail_refresh_token = credentials.refresh_token or email_settings.gmail_refresh_token
#                 email_settings.gmail_access_token = credentials.token
#                 email_settings.gmail_token_expires_at = credentials.expiry
#                 email_settings.save()

#             logger.info(f"Gmail connected successfully for user {user_uid}")
#             return True

#         except Exception as e:
#             logger.error(f"OAuth callback error for user {state}: {str(e)}")
#             return False

#     def get_credentials(self, user_uid: str) -> Optional[Credentials]:
#         try:
#             email_settings = UserEmailSettings.objects.get(
#                 user_uid=user_uid,
#                 gmail_connected=True
#             )
#             if not email_settings.gmail_refresh_token:
#                 logger.warning(f"User {user_uid} has no refresh token. Reconnect Gmail.")
#                 return None

#             credentials = Credentials(
#                 token=email_settings.gmail_access_token,
#                 refresh_token=email_settings.gmail_refresh_token,
#                 token_uri="https://oauth2.googleapis.com/token",
#                 client_id=self.client_id,
#                 client_secret=self.client_secret,
#             )
#             if credentials.expired:
#                 credentials.refresh(Request())
#                 email_settings.gmail_access_token = credentials.token
#                 email_settings.gmail_token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=3600)
#                 email_settings.save()

#             return credentials

#         except UserEmailSettings.DoesNotExist:
#             logger.warning(f"No Gmail connection found for user {user_uid}")
#             return None
#         except Exception as e:
#             logger.error(f"Error getting credentials for user {user_uid}: {str(e)}")
#             return None

#     # ----------------------
#     # Utility Methods
#     # ----------------------
#     def get_company_domains_for_user(self, user_uid: str) -> List[str]:
#         applications = Application.objects.filter(user_uid=user_uid, email_tracking_enabled=True)
#         domains = set()
#         for app in applications:
#             company = app.company_name.lower()
#             company_clean = company.replace(' ', '').replace('inc', '').replace('llc', '').replace('.', '')
#             domains.add(f"{company_clean}.com")
#             if app.company_email_domains:
#                 domains.update(app.company_email_domains)
#         return list(domains)

#     # ----------------------
#     # Gmail Email Search
#     # ----------------------
#     def search_job_related_emails(self, user_uid: str, days_back: int = 7) -> List[Dict]:
#         credentials = self.get_credentials(user_uid)
#         if not credentials:
#             return []

#         try:
#             service = build('gmail', 'v1', credentials=credentials)
#             company_domains = self.get_company_domains_for_user(user_uid)
#             date_filter = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime('%Y/%m/%d')

#             search_queries = [f"from:{domain}" for domain in company_domains[:10]]

#             job_keywords = [
#                 "job application", "interview", "position", "candidate",
#                 "application received", "thank you for applying", "next steps",
#                 "offer", "rejection", "unfortunately", "pleased to inform",
#                 "job opportunity", "career opportunity", "employment", "hiring",
#                 "selected", "shortlisted", "application update", "final round",
#                 "technical interview", "hr interview", "schedule interview", 
#                 "assessment", "evaluation", "onboarding", "welcome", "contract offer",
#                 "salary", "joining", "internship", "full-time", "part-time"
#             ]

#             search_queries += [f'subject:"{keyword}"' for keyword in job_keywords]
#             query = f"after:{date_filter} ({' OR '.join(search_queries)})" if search_queries else f"after:{date_filter} (job OR application OR interview OR position OR candidate)"

#             logger.info(f"Gmail search query for user {user_uid}: {query}")

#             results = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
#             messages = results.get('messages', [])
#             logger.info(f"Found {len(messages)} potential job-related emails for user {user_uid}")

#             email_data = []
#             for message in messages:
#                 try:
#                     msg_detail = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
#                     parsed_email = self._parse_email_message(msg_detail)
#                     if parsed_email:
#                         matched_app = self.match_email_to_application(user_uid, parsed_email)
#                         parsed_email['matched_application'] = matched_app.id if matched_app else None
#                         email_data.append(parsed_email)
#                 except Exception as e:
#                     logger.warning(f"Failed to fetch email {message['id']}: {str(e)}")
#                     continue

#             return email_data

#         except Exception as e:
#             logger.error(f"Error searching emails for user {user_uid}: {str(e)}")
#             return []

#     # ----------------------
#     # Email Parsing
#     # ----------------------
#     def _parse_email_message(self, message: Dict) -> Optional[Dict]:
#         try:
#             headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
#             body = self._extract_email_body(message['payload'])
#             internal_date = int(message['internalDate']) / 1000
#             received_date = datetime.fromtimestamp(internal_date, tz=timezone.utc)
#             return {
#                 'email_id': message['id'],
#                 'thread_id': message['threadId'],
#                 'sender_email': headers.get('From', '').split('<')[-1].rstrip('>').strip(),
#                 'sender_name': headers.get('From', '').split('<')[0].strip().strip('"'),
#                 'subject': headers.get('Subject', ''),
#                 'snippet': message.get('snippet', ''),
#                 'body': body[:5000],
#                 'received_date': received_date,
#                 'labels': message.get('labelIds', [])
#             }
#         except Exception as e:
#             logger.error(f"Error parsing email message: {str(e)}")
#             return None

#     def _extract_email_body(self, payload: Dict) -> str:
#         body = ""
#         if 'parts' in payload:
#             for part in payload['parts']:
#                 mime_type = part.get('mimeType', 'text/plain')
#                 data = part.get('body', {}).get('data', '')
#                 if data:
#                     decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
#                     if mime_type == 'text/plain':
#                         return decoded
#                     elif mime_type == 'text/html' and not body:
#                         soup = BeautifulSoup(decoded, "html.parser")
#                         body = soup.get_text()
#         else:
#             data = payload.get('body', {}).get('data', '')
#             if data:
#                 decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
#                 if payload.get('mimeType') == 'text/plain':
#                     return decoded
#                 elif payload.get('mimeType') == 'text/html':
#                     soup = BeautifulSoup(decoded, "html.parser")
#                     body = soup.get_text()
#         return body

#     # ----------------------
#     # Disconnect Gmail
#     # ----------------------
#     def disconnect_gmail(self, user_uid: str) -> bool:
#         try:
#             UserEmailSettings.objects.filter(user_uid=user_uid).update(
#                 gmail_connected=False,
#                 gmail_access_token=None,
#                 gmail_refresh_token=None,
#                 gmail_token_expires_at=None
#             )
#             logger.info(f"Gmail disconnected for user {user_uid}")
#             return True
#         except Exception as e:
#             logger.error(f"Error disconnecting Gmail for user {user_uid}: {str(e)}")
#             return False

#     # ----------------------
#     # Match Email to Application
#     # ----------------------
#     def match_email_to_application(self, user_uid: str, email_data):
#         if not isinstance(email_data, dict):
#             logger.warning(f"match_email_to_application received non-dict: {email_data}")
#             return None

#         subject = (email_data.get("subject") or "").lower()
#         body = (email_data.get("body") or "").lower()
#         sender = (email_data.get("sender_email") or "").lower()
#         combined_text = subject + " " + body

#         applications = Application.objects.filter(user_uid=user_uid)

#         job_keywords = [
#             "job application", "interview", "position", "candidate",
#             "application received", "thank you for applying", "next steps",
#             "offer", "rejection", "unfortunately", "pleased to inform",
#             "job opportunity", "career opportunity", "employment", "hiring",
#             "selected", "shortlisted", "application update", "final round",
#             "technical interview", "hr interview", "schedule interview", 
#             "assessment", "evaluation", "onboarding", "welcome", "contract offer",
#             "salary", "joining", "internship", "full-time", "part-time"
#         ]

#         # 1️⃣ Domain match
#         for app in applications:
#             if app.company_email_domains:
#                 for domain in app.company_email_domains:
#                     domain = domain.lower()
#                     if domain in sender or fuzz.partial_ratio(domain, sender) > 50:
#                         return app

#         # 2️⃣ Company name match
#         for app in applications:
#             if app.company_name:
#                 company_name = app.company_name.lower()
#                 if fuzz.partial_ratio(company_name, combined_text) > 50:
#                     return app

#         # 3️⃣ Job title match
#         for app in applications:
#             if app.job_title:
#                 job_title = app.job_title.lower()
#                 if fuzz.partial_ratio(job_title, combined_text) > 50:
#                     return app

#         # 4️⃣ Keyword match (optional)
#         for keyword in job_keywords:
#             if keyword.lower() in combined_text:
#                 return None

#         return None



import os
import logging
import base64
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from django.conf import settings
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

from .models import UserEmailSettings, Application, EmailLog

logger = logging.getLogger('applications.email_services')


class GmailService:
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid",
    ]

    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI

    # ----------------------
    # OAuth Methods
    # ----------------------
    def get_oauth_url(self, user_uid: str) -> str:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uris": [self.redirect_uri],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES,
            redirect_uri=self.redirect_uri
        )
        auth_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent',
            state=user_uid
        )
        return auth_url

    def handle_oauth_callback(self, code: str, state: str) -> bool:
        try:
            user_uid = state
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "redirect_uris": [self.redirect_uri],
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                scopes=self.SCOPES,
                redirect_uri=self.redirect_uri
            )
            flow.fetch_token(code=code)
            credentials = flow.credentials

            email_settings, created = UserEmailSettings.objects.get_or_create(
                user_uid=user_uid,
                defaults={
                    'gmail_connected': True,
                    'gmail_refresh_token': credentials.refresh_token,
                    'gmail_access_token': credentials.token,
                    'gmail_token_expires_at': credentials.expiry,
                }
            )
            if not created:
                email_settings.gmail_connected = True
                email_settings.gmail_refresh_token = credentials.refresh_token or email_settings.gmail_refresh_token
                email_settings.gmail_access_token = credentials.token
                email_settings.gmail_token_expires_at = credentials.expiry
                email_settings.save()

            logger.info(f"Gmail connected successfully for user {user_uid}")
            return True

        except Exception as e:
            logger.error(f"OAuth callback error for user {state}: {str(e)}")
            return False

    def get_credentials(self, user_uid: str) -> Optional[Credentials]:
        try:
            email_settings = UserEmailSettings.objects.get(
                user_uid=user_uid,
                gmail_connected=True
            )
            if not email_settings.gmail_refresh_token:
                logger.warning(f"User {user_uid} has no refresh token. Reconnect Gmail.")
                return None

            credentials = Credentials(
                token=email_settings.gmail_access_token,
                refresh_token=email_settings.gmail_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
            )
            if credentials.expired:
                credentials.refresh(Request())
                email_settings.gmail_access_token = credentials.token
                email_settings.gmail_token_expires_at = datetime.now(timezone.utc) + timedelta(seconds=3600)
                email_settings.save()

            return credentials

        except UserEmailSettings.DoesNotExist:
            logger.warning(f"No Gmail connection found for user {user_uid}")
            return None
        except Exception as e:
            logger.error(f"Error getting credentials for user {user_uid}: {str(e)}")
            return None

    # ----------------------
    # Utility Methods
    # ----------------------
    def get_company_domains_for_user(self, user_uid: str) -> List[str]:
        applications = Application.objects.filter(user_uid=user_uid, email_tracking_enabled=True)
        domains = set()
        for app in applications:
            company = app.company_name.lower()
            company_clean = company.replace(' ', '').replace('inc', '').replace('llc', '').replace('.', '')
            domains.add(f"{company_clean}.com")
            if app.company_email_domains:
                domains.update(app.company_email_domains)
        return list(domains)

    # ----------------------
    # Enhanced Gmail Email Search
    # ----------------------
    def search_job_related_emails(self, user_uid: str, days_back: int = 7) -> List[Dict]:
        """
        Search for job-related emails across all Gmail folders including drafts, spam, etc.
        """
        credentials = self.get_credentials(user_uid)
        if not credentials:
            return []

        try:
            service = build('gmail', 'v1', credentials=credentials)
            company_domains = self.get_company_domains_for_user(user_uid)
            date_filter = (datetime.now(timezone.utc) - timedelta(days=days_back)).strftime('%Y/%m/%d')

            # Enhanced job-related keywords with better categorization
            job_keywords = [
                # Application status
                "application received", "thank you for applying", "application update", 
                "application status", "we received your application",
                
                # Interview related
                "interview", "schedule interview", "interview invitation", "interview confirmation",
                "technical interview", "phone interview", "video interview", "final interview",
                "interview feedback", "next round", "coding challenge", "assessment",
                
                # Positive outcomes
                "congratulations", "pleased to inform", "offer", "job offer", "salary offer",
                "contract", "welcome to", "onboarding", "start date", "joining", "selected",
                
                # Negative outcomes
                "unfortunately", "regret to inform", "not selected", "unsuccessful",
                "position has been filled", "moving forward with other candidates",
                
                # General job terms
                "position", "role", "candidate", "employment", "career opportunity",
                "job opportunity", "hiring", "recruitment", "hr", "human resources",
                "recruiter", "talent acquisition", "resume", "cv"
            ]

            # Build search queries with improved logic
            search_parts = []
            
            # 1. Company domain searches (limit to top 20 for comprehensive search)
            if company_domains:
                recent_domains = company_domains[:20]
                domain_queries = [f"from:{domain}" for domain in recent_domains]
                search_parts.extend(domain_queries)
            
            # 2. Keyword searches in subject and body
            keyword_queries = []
            for keyword in job_keywords:
                # Search in subject (higher relevance)
                keyword_queries.append(f'subject:"{keyword}"')
                # Also search in body for comprehensive coverage
                keyword_queries.append(f'"{keyword}"')
            
            search_parts.extend(keyword_queries)
            
            # 3. Build final query searching ALL folders (inbox, sent, drafts, spam, etc.)
            base_query_parts = []
            
            # Date filter
            base_query_parts.append(f"after:{date_filter}")
            
            # Minimal exclusions to allow comprehensive search
            exclusions = [
                "-from:newsletter", "-subject:unsubscribe",
                "-subject:newsletter", "-subject:promotional"
            ]
            base_query_parts.extend(exclusions)
            
            # Combine with OR logic for search terms
            if search_parts:
                search_query = f"({' OR '.join(search_parts)})"
                full_query = f"{' '.join(base_query_parts)} {search_query}"
            else:
                # Fallback query if no specific domains/keywords
                fallback_terms = ["job", "application", "interview", "position", "career", "employment"]
                fallback_query = f"({' OR '.join(fallback_terms)})"
                full_query = f"{' '.join(base_query_parts)} {fallback_query}"

            logger.info(f"Gmail comprehensive search query for user {user_uid}: {full_query}")

            # Execute search with pagination for comprehensive results
            all_messages = []
            page_token = None
            max_pages = 5  # Increased for more comprehensive search
            current_page = 0
            
            while current_page < max_pages:
                try:
                    if page_token:
                        results = service.users().messages().list(
                            userId='me', 
                            q=full_query, 
                            maxResults=100,  # Increased for better coverage
                            pageToken=page_token
                        ).execute()
                    else:
                        results = service.users().messages().list(
                            userId='me', 
                            q=full_query, 
                            maxResults=100
                        ).execute()
                    
                    messages = results.get('messages', [])
                    all_messages.extend(messages)
                    
                    page_token = results.get('nextPageToken')
                    current_page += 1
                    
                    if not page_token:
                        break
                        
                except Exception as e:
                    logger.warning(f"Error fetching page {current_page}: {str(e)}")
                    break

            logger.info(f"Found {len(all_messages)} potential job-related emails across all folders for user {user_uid}")

            # Process emails with improved parsing
            email_data = []
            processed_count = 0
            max_emails_to_process = 200  # Increased for comprehensive search
            
            for message in all_messages:
                if processed_count >= max_emails_to_process:
                    break
                    
                try:
                    msg_detail = service.users().messages().get(
                        userId='me', 
                        id=message['id'], 
                        format='full'
                    ).execute()
                    
                    parsed_email = self._parse_email_message(msg_detail)
                    if parsed_email and self._is_valid_job_email(parsed_email):
                        # Check if we already processed this email recently
                        if not self._is_duplicate_email(user_uid, parsed_email):
                            matched_app = self.match_email_to_application(user_uid, parsed_email)
                            parsed_email['matched_application'] = matched_app.id if matched_app else None
                            parsed_email['relevance_score'] = self._calculate_relevance_score(parsed_email, job_keywords)
                            parsed_email['email_source'] = self._identify_email_source(parsed_email)
                            email_data.append(parsed_email)
                            processed_count += 1
                            
                except Exception as e:
                    logger.warning(f"Failed to fetch email {message['id']}: {str(e)}")
                    continue

            # Sort by relevance score and date
            email_data.sort(key=lambda x: (x.get('relevance_score', 0), x.get('received_date')), reverse=True)
            
            logger.info(f"Successfully processed {len(email_data)} job-related emails for user {user_uid}")
            return email_data

        except Exception as e:
            logger.error(f"Error searching emails for user {user_uid}: {str(e)}")
            return []

    # ----------------------
    # Email Parsing
    # ----------------------
    def _parse_email_message(self, message: Dict) -> Optional[Dict]:
        try:
            headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
            body = self._extract_email_body(message['payload'])
            internal_date = int(message['internalDate']) / 1000
            received_date = datetime.fromtimestamp(internal_date, tz=timezone.utc)
            return {
                'email_id': message['id'],
                'thread_id': message['threadId'],
                'sender_email': headers.get('From', '').split('<')[-1].rstrip('>').strip(),
                'sender_name': headers.get('From', '').split('<')[0].strip().strip('"'),
                'subject': headers.get('Subject', ''),
                'snippet': message.get('snippet', ''),
                'body': body[:5000],
                'received_date': received_date,
                'labels': message.get('labelIds', [])
            }
        except Exception as e:
            logger.error(f"Error parsing email message: {str(e)}")
            return None

    def _extract_email_body(self, payload: Dict) -> str:
        body = ""
        if 'parts' in payload:
            for part in payload['parts']:
                mime_type = part.get('mimeType', 'text/plain')
                data = part.get('body', {}).get('data', '')
                if data:
                    try:
                        decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                        if mime_type == 'text/plain':
                            return decoded
                        elif mime_type == 'text/html' and not body:
                            soup = BeautifulSoup(decoded, "html.parser")
                            body = soup.get_text()
                    except Exception as e:
                        logger.warning(f"Error decoding email body part: {str(e)}")
                        continue
        else:
            data = payload.get('body', {}).get('data', '')
            if data:
                try:
                    decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    if payload.get('mimeType') == 'text/plain':
                        return decoded
                    elif payload.get('mimeType') == 'text/html':
                        soup = BeautifulSoup(decoded, "html.parser")
                        body = soup.get_text()
                except Exception as e:
                    logger.warning(f"Error decoding email body: {str(e)}")
        return body

    def _is_valid_job_email(self, email_data: Dict) -> bool:
        """
        Relaxed validation to allow more emails through since we're searching all folders
        """
        subject = (email_data.get("subject") or "").lower()
        body = (email_data.get("body") or "").lower()
        sender = (email_data.get("sender_email") or "").lower()
        
        # More lenient spam filtering since we want to include drafts and spam folder
        severe_spam_indicators = [
            "click here to win", "congratulations you've won", "nigerian prince",
            "transfer money", "lottery winner", "viagra", "casino", "bitcoin mining",
            "weight loss", "make money fast", "work from home scam"
        ]
        
        combined_text = f"{subject} {body} {sender}"
        
        # Only filter out severe spam
        for indicator in severe_spam_indicators:
            if indicator in combined_text:
                return False
        
        # More inclusive job-related context (allowing broader terms)
        job_indicators = [
            "job", "position", "role", "interview", "application", "candidate",
            "employment", "career", "hiring", "hr", "human resources", 
            "recruiter", "recruitment", "offer", "onboarding", "work",
            "company", "team", "manager", "director", "opportunity",
            "resume", "cv", "experience", "skills", "qualification",
            "salary", "benefits", "remote", "office", "full-time", "part-time"
        ]
        
        return any(indicator in combined_text for indicator in job_indicators)

    def _calculate_relevance_score(self, email_data: Dict, job_keywords: List[str]) -> int:
        """
        Calculate relevance score for ranking emails with enhanced scoring
        """
        subject = (email_data.get("subject") or "").lower()
        body = (email_data.get("body") or "").lower()
        sender = (email_data.get("sender_email") or "").lower()
        labels = email_data.get('labels', [])
        
        score = 0
        
        # Subject line matches are more important
        for keyword in job_keywords:
            if keyword in subject:
                score += 3
            elif keyword in body:
                score += 1
        
        # HR/recruiting domains get bonus points
        hr_domains = ["hr", "recruiting", "talent", "careers", "jobs", "people"]
        if any(domain in sender for domain in hr_domains):
            score += 3
        
        # Email from known job platforms
        job_platforms = ["linkedin", "indeed", "glassdoor", "monster", "ziprecruiter"]
        if any(platform in sender for platform in job_platforms):
            score += 2
        
        # Bonus for emails in important folders
        if 'IMPORTANT' in labels:
            score += 2
        if 'STARRED' in labels:
            score += 1
        
        # Recent emails get slight bonus
        if email_data.get('received_date'):
            days_old = (datetime.now(timezone.utc) - email_data['received_date']).days
            if days_old <= 1:
                score += 2
            elif days_old <= 3:
                score += 1
        
        # Penalty for spam folder (but still include)
        if 'SPAM' in labels:
            score -= 1
        
        return max(0, score)  # Ensure non-negative score

    def _identify_email_source(self, email_data: Dict) -> str:
        """
        Identify which folder/source the email came from
        """
        labels = email_data.get('labels', [])
        
        if 'INBOX' in labels:
            return 'inbox'
        elif 'SENT' in labels:
            return 'sent'
        elif 'DRAFT' in labels:
            return 'draft'
        elif 'SPAM' in labels:
            return 'spam'
        elif 'TRASH' in labels:
            return 'trash'
        else:
            return 'other'

    def _is_duplicate_email(self, user_uid: str, email_data: Dict) -> bool:
        """
        Check if we've already processed this email recently
        """
        try:
            email_id = email_data.get('email_id')
            if not email_id:
                return False
                
            # Check if email was logged in the last 24 hours
            recent_cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            
            return EmailLog.objects.filter(
                user_uid=user_uid,
                email_id=email_id,
                processed_at__gte=recent_cutoff
            ).exists()
            
        except Exception as e:
            logger.warning(f"Error checking duplicate email: {str(e)}")
            return False

    # ----------------------
    # Disconnect Gmail
    # ----------------------
    def disconnect_gmail(self, user_uid: str) -> bool:
        try:
            UserEmailSettings.objects.filter(user_uid=user_uid).update(
                gmail_connected=False,
                gmail_access_token=None,
                gmail_refresh_token=None,
                gmail_token_expires_at=None
            )
            logger.info(f"Gmail disconnected for user {user_uid}")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting Gmail for user {user_uid}: {str(e)}")
            return False

    # ----------------------
    # Enhanced Email Matching
    # ----------------------
    def match_email_to_application(self, user_uid: str, email_data):
        """
        Enhanced matching with better fuzzy logic and scoring
        """
        if not isinstance(email_data, dict):
            logger.warning(f"match_email_to_application received non-dict: {email_data}")
            return None

        subject = (email_data.get("subject") or "").lower()
        body = (email_data.get("body") or "").lower()
        sender = (email_data.get("sender_email") or "").lower()
        combined_text = f"{subject} {body}"

        applications = Application.objects.filter(user_uid=user_uid)
        
        best_match = None
        best_score = 0

        for app in applications:
            match_score = 0
            
            # 1️⃣ Domain match (highest priority)
            if app.company_email_domains:
                for domain in app.company_email_domains:
                    domain = domain.lower()
                    if domain in sender:
                        match_score += 50
                    elif fuzz.partial_ratio(domain, sender) > 70:
                        match_score += 30

            # 2️⃣ Company name match
            if app.company_name:
                company_name = app.company_name.lower()
                company_ratio = fuzz.partial_ratio(company_name, combined_text)
                if company_ratio > 70:
                    match_score += 40
                elif company_ratio > 50:
                    match_score += 20

            # 3️⃣ Job title match
            if app.job_title:
                job_title = app.job_title.lower()
                title_ratio = fuzz.partial_ratio(job_title, combined_text)
                if title_ratio > 70:
                    match_score += 30
                elif title_ratio > 50:
                    match_score += 15

            # 4️⃣ Application date proximity bonus
            if app.applied_date:
                days_diff = abs((email_data.get('received_date', datetime.now(timezone.utc)) - app.applied_date).days)
                if days_diff <= 30:  # Within 30 days
                    match_score += 10
                elif days_diff <= 90:  # Within 90 days
                    match_score += 5

            # Update best match if this score is higher
            if match_score > best_score and match_score > 25:  # Minimum threshold
                best_match = app
                best_score = match_score

        return best_match