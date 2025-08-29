# from celery import shared_task
# from django.db import transaction
# from django.utils import timezone
# from datetime import datetime, timedelta
# import logging

# from .models import JobFilter, Application, UserEmailSettings, EmailLog, TimelineEvent
# from .services.job_fetcher import JobFetcherService
# from .email_services import GmailService
# from .ai_services import GeminiEmailAnalyzer

# logger = logging.getLogger('applications.tasks')


# def _salary_range_str(minv, maxv):
#     if minv and maxv:
#         return f"{minv}-{maxv}"
#     if minv:
#         return f"{minv}+"
#     if maxv:
#         return f"up to {maxv}"
#     return ""


# @shared_task
# def fetch_jobs_daily():
#     """
#     Daily job fetcher:
#     - For each saved JobFilter
#     - Fetch from configured providers
#     - Save to Job table
#     - Also create/ensure an Application in 'saved' status for that user + job URL
#     """
#     service = JobFetcherService()
#     total_new_jobs = 0
#     total_new_apps = 0

#     logger.info("Starting daily job fetch. Checking for saved filters...")

#     filters = JobFilter.objects.all()
#     logger.info(f"Found {len(filters)} saved filters")

#     for f in filters:
#         providers = f.providers or ["jooble", "adzuna"]
#         logger.info(f"Processing filter for user {f.user_uid}: keywords={f.keywords}, locations={f.locations}, providers={providers}")

#         for kw in (f.keywords or []):
#             for loc in (f.locations or []):
#                 logger.info(f"Fetching jobs for keyword: '{kw}' in location: '{loc}'")

#                 jobs = service.fetch_all(kw, loc, providers=providers)
#                 created = service.save_jobs(jobs)
#                 total_new_jobs += created

#                 logger.info(f"Creating applications for user {f.user_uid} from {len(jobs)} jobs")

#                 for j in jobs:
#                     url = j.get("link")
#                     title = j.get("title") or "Untitled"
#                     company = j.get("company") or "Unknown"
#                     location = j.get("location") or ""
#                     salary = _salary_range_str(j.get("salary_min"), j.get("salary_max"))

#                     with transaction.atomic():
#                         app, was_created = Application.objects.get_or_create(
#                             user_uid=f.user_uid,
#                             job_posting_url=url,
#                             defaults={
#                                 "company_name": company,
#                                 "job_title": title,
#                                 "location": location,
#                                 "salary_range": salary,
#                                 "status": "saved",
#                             }
#                         )
#                         if was_created:
#                             total_new_apps += 1
#                             logger.info(f"Created new application: {title} at {company} for user {f.user_uid}")
#                         else:
#                             logger.debug(f"Application already exists: {title} at {company} for user {f.user_uid}")

#     logger.info(f"Daily job fetch completed. New Jobs: {total_new_jobs} | New Saved Applications: {total_new_apps}")
#     return {"jobs": total_new_jobs, "applications": total_new_apps}


# @shared_task
# def process_user_emails(user_uid: str):
#     """
#     Process emails for a specific user to update job application statuses
#     """
#     try:
#         # Check if user has email tracking enabled
#         try:
#             email_settings = UserEmailSettings.objects.get(user_uid=user_uid, gmail_connected=True)
#         except UserEmailSettings.DoesNotExist:
#             logger.info(f"Email tracking not enabled for user {user_uid}")
#             return {"processed": 0, "updated": 0}

#         gmail_service = GmailService()
#         ai_service = GeminiEmailAnalyzer()

#         # Search for job-related emails from last 7 days
#         emails = gmail_service.search_job_related_emails(user_uid, days_back=7)
#         logger.info(f"Found {len(emails)} emails to process for user {user_uid}")

#         processed_count = 0
#         updated_count = 0

#         for email_data in emails:
#             try:
#                 # Skip already processed emails
#                 if EmailLog.objects.filter(email_id=email_data['email_id']).exists():
#                     logger.debug(f"Email {email_data['email_id']} already processed, skipping")
#                     continue

#                 # Match email to application
#                 application = gmail_service.match_email_to_application( user_uid, email_data)
#                 if not application:
#                     logger.debug(f"No application match found for email {email_data['email_id']}")
#                     continue

#                 # Prepare data for AI
#                 app_data = {
#                     'job_title': application.job_title,
#                     'company_name': application.company_name,
#                     'application_date': application.application_date,
#                     'status': application.status
#                 }

#                 # Analyze email content with AI
#                 analysis = ai_service.analyze_job_email(email_data, app_data)
#                 if not analysis:
#                     logger.warning(f"AI analysis failed for email {email_data['email_id']}")
#                     continue

#                 # Create EmailLog entry
#                 email_log = EmailLog.objects.create(
#                     application=application,
#                     user_uid=user_uid,
#                     email_id=email_data['email_id'],
#                     thread_id=email_data.get('thread_id'),
#                     sender_email=email_data['sender_email'],
#                     sender_name=email_data.get('sender_name'),
#                     subject=email_data['subject'],
#                     snippet=email_data.get('snippet', ''),
#                     received_date=email_data.get('received_date') or timezone.now(),
#                     classification=analysis.get('classification'),
#                     confidence_score=analysis.get('confidence'),
#                     ai_analysis=analysis,
#                     suggested_status=analysis.get('suggested_status')
#                 )

#                 # Create timeline event for email
#                 TimelineEvent.objects.create(
#                     application=application,
#                     event_type='email_received',
#                     title='Email Received',
#                     description=f"From: {email_data['sender_email']}\nSubject: {email_data['subject']}\n\nAI Analysis: {analysis.get('timeline_note', '')}",
#                     date=timezone.localdate(),
#                     completed=True,
#                     is_auto_generated=True,
#                     email_log=email_log
#                 )

#                 # Update application status if suggested
#                 new_status = analysis.get('suggested_status')
#                 if new_status and new_status != application.status:
#                     application.status = new_status
#                     application.save()

#                     TimelineEvent.objects.create(
#                         application=application,
#                         event_type='status_change',
#                         title=f'Status updated to {new_status}',
#                         description=f"Automatically updated based on email from {email_data['sender_email']}",
#                         date=timezone.localdate(),
#                         completed=True,
#                         is_auto_generated=True
#                     )

#                     updated_count += 1
#                     logger.info(f"Updated application {application.id} status to {new_status}")

#                 processed_count += 1

#             except Exception as e:
#                 logger.error(f"Error processing email {email_data.get('email_id', 'unknown')}: {str(e)}")
#                 continue

#         logger.info(f"Completed email processing for user {user_uid}: {processed_count} processed, {updated_count} updated")
#         return {"processed": processed_count, "updated": updated_count}

#     except Exception as e:
#         logger.error(f"Error processing emails for user {user_uid}: {str(e)}")
#         return {"processed": 0, "updated": 0}


# @shared_task
# def process_all_users_emails():
#     """
#     Process emails for all users with email tracking enabled
#     """
#     users_with_email = UserEmailSettings.objects.filter(
#         gmail_connected=True,
#         email_tracking_enabled=True
#     ).values_list('user_uid', flat=True)

#     total_processed = 0
#     total_updated = 0

#     for user_uid in users_with_email:
#         result = process_user_emails(user_uid)
#         total_processed += result.get('processed', 0)
#         total_updated += result.get('updated', 0)

#     logger.info(f"Completed email processing for all users: {total_processed} processed, {total_updated} updated")
#     return {"total_processed": total_processed, "total_updated": total_updated}




from celery import shared_task
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import logging

from .models import JobFilter, Application, UserEmailSettings, EmailLog, TimelineEvent
from .services.job_fetcher import JobFetcherService
from .email_services import GmailService
from .ai_services import GeminiEmailAnalyzer

logger = logging.getLogger('applications.tasks')


def _salary_range_str(minv, maxv):
    if minv and maxv:
        return f"{minv}-{maxv}"
    if minv:
        return f"{minv}+"
    if maxv:
        return f"up to {maxv}"
    return ""

@shared_task
def fetch_jobs_daily():
    from .services.job_fetcher import JobFetcherService
    service = JobFetcherService()
    # You can reuse your fetch_all and save_jobs logic
    # For brevity, just call fetch_jobs_periodic for now:
    return fetch_jobs_periodic()

@shared_task
def fetch_jobs_periodic():
    """
    Periodic job fetcher (for testing) every 2 minutes.
    - For each saved JobFilter
    - Fetch from configured providers
    - Save to Job table
    - Also create/ensure an Application in 'saved' status for that user + job URL
    """
    service = JobFetcherService()
    total_new_jobs = 0
    total_new_apps = 0

    logger.info("Starting periodic job fetch. Checking for saved filters...")

    filters = JobFilter.objects.all()
    logger.info(f"Found {len(filters)} saved filters")

    for f in filters:
        providers = f.providers or ["jooble", "adzuna"]
        logger.info(f"Processing filter for user {f.user_uid}: keywords={f.keywords}, locations={f.locations}, providers={providers}")

        for kw in (f.keywords or []):
            for loc in (f.locations or []):
                logger.info(f"Fetching jobs for keyword: '{kw}' in location: '{loc}'")

                jobs = service.fetch_all(kw, loc, providers=providers)
                created = service.save_jobs(jobs)
                total_new_jobs += created

                logger.info(f"Creating applications for user {f.user_uid} from {len(jobs)} jobs")

                for j in jobs:
                    url = j.get("link")
                    title = j.get("title") or "Untitled"
                    company = j.get("company") or "Unknown"
                    location = j.get("location") or ""
                    salary = _salary_range_str(j.get("salary_min"), j.get("salary_max"))

                    with transaction.atomic():
                        app, was_created = Application.objects.get_or_create(
                            user_uid=f.user_uid,
                            job_posting_url=url,
                            defaults={
                                "company_name": company,
                                "job_title": title,
                                "location": location,
                                "salary_range": salary,
                                "status": "saved",
                            }
                        )
                        if was_created:
                            total_new_apps += 1
                            logger.info(f"Created new application: {title} at {company} for user {f.user_uid}")
                        else:
                            logger.debug(f"Application already exists: {title} at {company} for user {f.user_uid}")

    logger.info(f"Periodic job fetch completed. New Jobs: {total_new_jobs} | New Saved Applications: {total_new_apps}")
    return {"jobs": total_new_jobs, "applications": total_new_apps}




@shared_task
def process_user_emails(user_uid: str):
    """
    Process emails for a specific user to update job application statuses
    """
    try:
        # Check if user has email tracking enabled
        try:
            email_settings = UserEmailSettings.objects.get(user_uid=user_uid, gmail_connected=True)
        except UserEmailSettings.DoesNotExist:
            logger.info(f"Email tracking not enabled for user {user_uid}")
            return {"processed": 0, "updated": 0}

        gmail_service = GmailService()
        ai_service = GeminiEmailAnalyzer()

        # Search for job-related emails from last 7 days
        emails = gmail_service.search_job_related_emails(user_uid, days_back=7)
        logger.info(f"Found {len(emails)} emails to process for user {user_uid}")

        processed_count = 0
        updated_count = 0

        for email_data in emails:
            try:
                # Skip already processed emails
                if EmailLog.objects.filter(email_id=email_data['email_id']).exists():
                    logger.debug(f"Email {email_data['email_id']} already processed, skipping")
                    continue

                # Match email to application
                application = gmail_service.match_email_to_application( user_uid, email_data)
                if not application:
                    logger.debug(f"No application match found for email {email_data['email_id']}")
                    continue

                # Prepare data for AI
                app_data = {
                    'job_title': application.job_title,
                    'company_name': application.company_name,
                    'application_date': application.application_date,
                    'status': application.status
                }

                # Analyze email content with AI
                analysis = ai_service.analyze_job_email(email_data, app_data)
                if not analysis:
                    logger.warning(f"AI analysis failed for email {email_data['email_id']}")
                    continue

                # Create EmailLog entry
                
                email_log, created = EmailLog.objects.update_or_create(
                    email_id=email_data['email_id'],
                    defaults={
                        "application": application,
                        "user_uid": user_uid,
                        "thread_id": email_data.get("thread_id"),
                        "sender_email": email_data["sender_email"],
                        "sender_name": email_data.get("sender_name"),
                        "subject": email_data["subject"],
                        "snippet": email_data.get("snippet", ""),
                        "received_date": email_data.get("received_date") or timezone.now(),
                        "classification": analysis.get("classification"),
                        "confidence_score": analysis.get("confidence"),
                        "ai_analysis": analysis,
                        "suggested_status": analysis.get("suggested_status"),
                        "processed": True,
                        "processed_at": timezone.now(),
                    }
                )

                # Create timeline event for email
                TimelineEvent.objects.create(
                    application=application,
                    event_type='email_received',
                    title='Email Received',
                    description=f"From: {email_data['sender_email']}\nSubject: {email_data['subject']}\n\nAI Analysis: {analysis.get('timeline_note', '')}",
                    date=timezone.localdate(),
                    completed=True,
                    is_auto_generated=True,
                    email_log=email_log
                )

                # Update application status if suggested
                new_status = analysis.get('suggested_status')
                if new_status and new_status != application.status:
                    application.status = new_status
                    application.save()

                    TimelineEvent.objects.create(
                        application=application,
                        event_type='status_change',
                        title=f'Status updated to {new_status}',
                        description=f"Automatically updated based on email from {email_data['sender_email']}",
                        date=timezone.localdate(),
                        completed=True,
                        is_auto_generated=True
                    )

                    updated_count += 1
                    logger.info(f"Updated application {application.id} status to {new_status}")

                processed_count += 1

            except Exception as e:
                logger.error(f"Error processing email {email_data.get('email_id', 'unknown')}: {str(e)}")
                continue

        logger.info(f"Completed email processing for user {user_uid}: {processed_count} processed, {updated_count} updated")
        return {"processed": processed_count, "updated": updated_count}

    except Exception as e:
        logger.error(f"Error processing emails for user {user_uid}: {str(e)}")
        return {"processed": 0, "updated": 0}


@shared_task
def process_all_users_emails():
    """
    Process emails for all users with email tracking enabled
    """
    users_with_email = UserEmailSettings.objects.filter(
        gmail_connected=True,
        email_tracking_enabled=True
    ).values_list('user_uid', flat=True)

    total_processed = 0
    total_updated = 0

    for user_uid in users_with_email:
        result = process_user_emails(user_uid)
        total_processed += result.get('processed', 0)
        total_updated += result.get('updated', 0)

    logger.info(f"Completed email processing for all users: {total_processed} processed, {total_updated} updated")
    return {"total_processed": total_processed, "total_updated": total_updated}
