# from celery import shared_task
# from django.db import transaction
# from .models import JobFilter, Application
# from .services.job_fetcher import JobFetcherService

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

#     for f in JobFilter.objects.all():
#         providers = f.providers or ["jooble", "adzuna"]
#         for kw in (f.keywords or []):
#             for loc in (f.locations or []):
#                 jobs = service.fetch_all(kw, loc, providers=providers)
#                 created = service.save_jobs(jobs)
#                 total_new_jobs += created

#                 # Create per-user "Saved" Application entries
#                 for j in jobs:
#                     url = j.get("link")
#                     title = j.get("title") or "Untitled"
#                     company = j.get("company") or "Unknown"
#                     location = j.get("location") or ""
#                     salary = _salary_range_str(j.get("salary_min"), j.get("salary_max"))

#                     with transaction.atomic():
#                         _, was_created = Application.objects.get_or_create(
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

#     print(f"[fetch_jobs_daily] New Jobs: {total_new_jobs} | New Saved Applications: {total_new_apps}")
#     return {"jobs": total_new_jobs, "applications": total_new_apps}


from celery import shared_task
from django.db import transaction
from .models import JobFilter, Application
from .services.job_fetcher import JobFetcherService

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
    """
    Daily job fetcher:
    - For each saved JobFilter
    - Fetch from configured providers
    - Save to Job table
    - Also create/ensure an Application in 'saved' status for that user + job URL
    """
    service = JobFetcherService()
    total_new_jobs = 0
    total_new_apps = 0
    
    print(f"[DEBUG] Starting daily job fetch. Checking for saved filters...")

    # Get all filters
    filters = JobFilter.objects.all()
    print(f"[DEBUG] Found {len(filters)} saved filters")

    for f in filters:
        providers = f.providers or ["jooble", "adzuna"]
        print(f"[DEBUG] Processing filter for user {f.user_uid}: keywords={f.keywords}, locations={f.locations}, providers={providers}")

        for kw in (f.keywords or []):
            for loc in (f.locations or []):
                print(f"[DEBUG] Fetching jobs for keyword: '{kw}' in location: '{loc}'")
                
                jobs = service.fetch_all(kw, loc, providers=providers)
                created = service.save_jobs(jobs)
                total_new_jobs += created

                # Create per-user "Saved" Application entries
                print(f"[DEBUG] Creating applications for user {f.user_uid} from {len(jobs)} jobs")
                
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
                            print(f"[DEBUG] Created new application: {title} at {company} for user {f.user_uid}")
                        else:
                            print(f"[DEBUG] Application already exists: {title} at {company} for user {f.user_uid}")

    print(f"[fetch_jobs_daily] New Jobs: {total_new_jobs} | New Saved Applications: {total_new_apps}")
    return {"jobs": total_new_jobs, "applications": total_new_apps}