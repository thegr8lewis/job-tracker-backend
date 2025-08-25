# import os
# import requests
# from datetime import datetime
# from typing import List, Dict, Any, Optional
# import json
# import time
# from urllib.parse import quote_plus

# from django.conf import settings
# from ..models import Job

# def _parse_iso(dt: Optional[str]) -> Optional[datetime]:
#     if not dt:
#         return None
#     try:
#         # Handle various date formats
#         if dt.endswith('Z'):
#             return datetime.fromisoformat(dt.replace("Z", "+00:00"))
#         return datetime.fromisoformat(dt)
#     except Exception:
#         return None

# class JobFetcherService:
#     """
#     Enhanced job fetcher with better error handling and additional sources
#     """
#     def __init__(self):
#         self.jooble_key = getattr(settings, "JOOBLE_API_KEY", None)
#         self.adzuna_app_id = getattr(settings, "ADZUNA_APP_ID", None)
#         self.adzuna_app_key = getattr(settings, "ADZUNA_APP_KEY", None)
#         self.rapidapi_key = getattr(settings, "RAPIDAPI_KEY", None)
#         self.workable_token = getattr(settings, "WORKABLE_TOKEN", None)
        
#         # Debug info
#         print(f"[DEBUG] API Keys Status:")
#         print(f"  Jooble: {'✓' if self.jooble_key else '✗'}")
#         print(f"  Adzuna: {'✓' if self.adzuna_app_id and self.adzuna_app_key else '✗'}")
#         print(f"  RapidAPI: {'✓' if self.rapidapi_key else '✗'}")

#     def fetch_from_jooble(self, keyword: str, location: str) -> List[Dict[str, Any]]:
#         """Enhanced Jooble fetcher with better error handling"""
#         if not self.jooble_key:
#             print("[DEBUG] Jooble: API key not set")
#             return []
        
#         url = f"https://jooble.org/api/{self.jooble_key}"
        
#         # Try different location formats
#         locations_to_try = [
#             location,
#             f"{location}, Kenya",
#             "Kenya",
#             "Nairobi, Kenya" if location.lower() != "nairobi" else location
#         ]
        
#         for loc in locations_to_try:
#             payload = {"keywords": keyword, "location": loc}
#             print(f"[DEBUG] Jooble: Trying location '{loc}'")
            
#             try:
#                 headers = {
#                     'Content-Type': 'application/json',
#                     'User-Agent': 'Mozilla/5.0 (compatible; JobBot/1.0)'
#                 }
                
#                 r = requests.post(url, json=payload, headers=headers, timeout=30)
#                 print(f"[DEBUG] Jooble: Status {r.status_code} for location '{loc}'")
                
#                 if r.status_code == 200:
#                     data = r.json()
#                     jobs_count = len(data.get("jobs", []))
#                     print(f"[DEBUG] Jooble: Found {jobs_count} jobs for '{loc}'")
                    
#                     if jobs_count > 0:
#                         jobs = []
#                         for j in data.get("jobs", []):
#                             job_data = {
#                                 "title": j.get("title"),
#                                 "company": j.get("company"),
#                                 "location": j.get("location"),
#                                 "salary_min": None,
#                                 "salary_max": None,
#                                 "link": j.get("link"),
#                                 "source": "jooble",
#                                 "posted_at": datetime.utcnow(),
#                                 "description": j.get("snippet", "")[:500]  # Truncate description
#                             }
#                             jobs.append(job_data)
                        
#                         return [x for x in jobs if x.get("title") and x.get("link")]
                
#                 elif r.status_code == 400:
#                     error_data = r.json()
#                     print(f"[DEBUG] Jooble: Bad request - {error_data}")
                
#                 time.sleep(1)  # Rate limiting
                
#             except requests.exceptions.RequestException as e:
#                 print(f"[DEBUG] Jooble: Request error for '{loc}': {str(e)}")
#                 continue
#             except Exception as e:
#                 print(f"[DEBUG] Jooble: General error for '{loc}': {str(e)}")
#                 continue
        
#         return []

#     def fetch_from_adzuna(self, keyword: str, location: str, country="ke") -> List[Dict[str, Any]]:
#         """Enhanced Adzuna fetcher with multiple country codes"""
#         if not (self.adzuna_app_id and self.adzuna_app_key):
#             print("[DEBUG] Adzuna: Credentials not set")
#             return []
        
#         # Try different country codes and locations
#         countries_to_try = ["ke", "gb", "us"]  # Kenya, UK (for international), US
#         locations_to_try = [
#             location,
#             f"{location} Kenya",
#             "Nairobi",
#             "Kenya",
#             ""  # Empty location to get all results
#         ]
        
#         for country_code in countries_to_try:
#             for loc in locations_to_try:
#                 url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
#                 params = {
#                     "app_id": self.adzuna_app_id,
#                     "app_key": self.adzuna_app_key,
#                     "what": keyword,
#                     "where": loc,
#                     "results_per_page": 50,
#                     "content_type": "application/json",
#                     "sort_by": "date"
#                 }
                
#                 # Remove empty params
#                 params = {k: v for k, v in params.items() if v}
                
#                 print(f"[DEBUG] Adzuna: Trying {country_code.upper()} with location '{loc}'")
                
#                 try:
#                     r = requests.get(url, params=params, timeout=30)
#                     print(f"[DEBUG] Adzuna: Status {r.status_code}")
#                     print(f"[DEBUG] Adzuna: URL {r.url}")
                    
#                     if r.status_code == 200:
#                         data = r.json()
#                         results_count = len(data.get("results", []))
#                         print(f"[DEBUG] Adzuna: Found {results_count} results")
                        
#                         if results_count > 0:
#                             jobs = []
#                             for j in data.get("results", []):
#                                 salary_min = j.get("salary_min")
#                                 salary_max = j.get("salary_max")
                                
#                                 job_data = {
#                                     "title": j.get("title"),
#                                     "company": (j.get("company") or {}).get("display_name"),
#                                     "location": (j.get("location") or {}).get("display_name"),
#                                     "salary_min": salary_min,
#                                     "salary_max": salary_max,
#                                     "link": j.get("redirect_url"),
#                                     "source": f"adzuna_{country_code}",
#                                     "posted_at": _parse_iso(j.get("created")),
#                                     "description": j.get("description", "")[:500]
#                                 }
#                                 jobs.append(job_data)
                            
#                             return [x for x in jobs if x.get("title") and x.get("link")]
                    
#                     elif r.status_code == 403:
#                         print(f"[DEBUG] Adzuna: Forbidden - check API credentials")
#                     elif r.status_code == 429:
#                         print(f"[DEBUG] Adzuna: Rate limited, waiting...")
#                         time.sleep(5)
#                     else:
#                         print(f"[DEBUG] Adzuna: HTTP {r.status_code} - {r.text[:200]}")
                    
#                     time.sleep(1)  # Rate limiting
                    
#                 except Exception as e:
#                     print(f"[DEBUG] Adzuna: Error for {country_code}/{loc}: {str(e)}")
#                     continue
        
#         return []

#     def fetch_from_rapidapi_jsearch(self, keyword: str, location: str) -> List[Dict[str, Any]]:
#         """Fetch from JSearch API via RapidAPI (popular job search API)"""
#         if not self.rapidapi_key:
#             print("[DEBUG] RapidAPI: Key not set")
#             return []
        
#         url = "https://jsearch.p.rapidapi.com/search"
        
#         # Try different query formats
#         queries_to_try = [
#             f"{keyword} in {location}",
#             f"{keyword} Kenya",
#             f"{keyword} Nairobi",
#             keyword
#         ]
        
#         for query in queries_to_try:
#             params = {
#                 "query": query,
#                 "page": "1",
#                 "num_pages": "1",
#                 "date_posted": "all"
#             }
            
#             headers = {
#                 "X-RapidAPI-Key": self.rapidapi_key,
#                 "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
#             }
            
#             print(f"[DEBUG] RapidAPI JSearch: Trying query '{query}'")
            
#             try:
#                 r = requests.get(url, headers=headers, params=params, timeout=30)
#                 print(f"[DEBUG] RapidAPI JSearch: Status {r.status_code}")
                
#                 if r.status_code == 200:
#                     data = r.json()
#                     jobs_data = data.get("data", [])
#                     print(f"[DEBUG] RapidAPI JSearch: Found {len(jobs_data)} jobs")
                    
#                     if len(jobs_data) > 0:
#                         jobs = []
#                         for j in jobs_data:
#                             job_data = {
#                                 "title": j.get("job_title"),
#                                 "company": j.get("employer_name"),
#                                 "location": j.get("job_city", "") + ", " + j.get("job_country", ""),
#                                 "salary_min": None,  # Usually not provided
#                                 "salary_max": None,
#                                 "link": j.get("job_apply_link"),
#                                 "source": "jsearch_rapidapi",
#                                 "posted_at": _parse_iso(j.get("job_posted_at_datetime_utc")),
#                                 "description": j.get("job_description", "")[:500]
#                             }
#                             if job_data["title"] and job_data["link"]:
#                                 jobs.append(job_data)
                        
#                         return jobs
                
#                 elif r.status_code == 429:
#                     print("[DEBUG] RapidAPI JSearch: Rate limited")
#                     break
#                 else:
#                     print(f"[DEBUG] RapidAPI JSearch: Error {r.status_code}")
                
#                 time.sleep(1)
                
#             except Exception as e:
#                 print(f"[DEBUG] RapidAPI JSearch: Error: {str(e)}")
#                 continue
        
#         return []

#     def fetch_from_rapidapi(self, keyword: str, location: str) -> List[Dict[str, Any]]:
#         """Wrapper for RapidAPI sources"""
#         return self.fetch_from_rapidapi_jsearch(keyword, location)

#     def fetch_from_workable(self, keyword: str, location: str) -> List[Dict[str, Any]]:
#         """Placeholder for Workable - requires company subdomain"""
#         print("[DEBUG] Workable: Not implemented (requires company subdomain)")
#         return []

#     def fetch_all(self, keyword: str, location: str, providers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
#         """Enhanced orchestration with better error handling"""
#         providers = providers or ["jooble", "adzuna", "rapidapi"]
#         results: List[Dict[str, Any]] = []
        
#         print(f"\n[DEBUG] === JOB SEARCH SESSION ===")
#         print(f"[DEBUG] Keyword: '{keyword}'")
#         print(f"[DEBUG] Location: '{location}'")
#         print(f"[DEBUG] Providers: {providers}")
#         print(f"[DEBUG] ============================\n")

#         for provider in providers:
#             print(f"\n[DEBUG] --- Starting {provider.upper()} ---")
            
#             try:
#                 if provider == "jooble":
#                     provider_results = self.fetch_from_jooble(keyword, location)
#                 elif provider == "adzuna":
#                     provider_results = self.fetch_from_adzuna(keyword, location)
#                 elif provider == "rapidapi":
#                     provider_results = self.fetch_from_rapidapi(keyword, location)
#                 elif provider == "workable":
#                     provider_results = self.fetch_from_workable(keyword, location)
#                 else:
#                     print(f"[DEBUG] Unknown provider: {provider}")
#                     continue
                
#                 results.extend(provider_results)
#                 print(f"[DEBUG] {provider.upper()}: Added {len(provider_results)} jobs")
                
#             except Exception as e:
#                 print(f"[DEBUG] {provider.upper()}: Fatal error - {str(e)}")
#                 continue
            
#             print(f"[DEBUG] --- Finished {provider.upper()} ---\n")

#         print(f"[DEBUG] Total jobs before deduplication: {len(results)}")

#         # Enhanced deduplication
#         seen_links = set()
#         seen_titles = set()
#         unique = []
        
#         for job in results:
#             link = job.get("link")
#             title = job.get("title", "").lower().strip()
#             company = job.get("company", "").lower().strip()
            
#             # Create a unique identifier
#             job_signature = f"{title}::{company}"
            
#             if link and link not in seen_links and job_signature not in seen_titles:
#                 seen_links.add(link)
#                 seen_titles.add(job_signature)
#                 unique.append(job)
        
#         print(f"[DEBUG] Total unique jobs after deduplication: {len(unique)}")
        
#         # Debug: Show sample results
#         if unique:
#             print(f"[DEBUG] Sample job: {unique[0].get('title')} at {unique[0].get('company')}")
        
#         return unique

#     def save_jobs(self, jobs: List[Dict[str, Any]]) -> int:
#         """Enhanced job saving with better error handling"""
#         created = 0
#         updated = 0
#         errors = 0
        
#         print(f"[DEBUG] Attempting to save {len(jobs)} jobs")
        
#         for i, job in enumerate(jobs, 1):
#             if not job.get("link"):
#                 errors += 1
#                 print(f"[DEBUG] Job {i}: Skipping - no link")
#                 continue
            
#             try:
#                 defaults = {
#                     "title": (job.get("title") or "")[:200],  # Ensure title fits DB field
#                     "company": (job.get("company") or "")[:100],
#                     "location": (job.get("location") or "")[:100],
#                     "salary_min": job.get("salary_min"),
#                     "salary_max": job.get("salary_max"),
#                     "source": (job.get("source") or "")[:50],
#                     "posted_at": job.get("posted_at") or datetime.utcnow(),
#                 }
                
#                 # Add description if your model has it
#                 if hasattr(Job, 'description'):
#                     defaults["description"] = job.get("description", "")[:1000]
                
#                 obj, was_created = Job.objects.get_or_create(
#                     link=job["link"][:500],  # Ensure URL fits
#                     defaults=defaults
#                 )
                
#                 if was_created:
#                     created += 1
#                     print(f"[DEBUG] Job {i}: CREATED - {obj.title[:50]}... at {obj.company}")
#                 else:
#                     updated += 1
#                     print(f"[DEBUG] Job {i}: EXISTS - {obj.title[:50]}... at {obj.company}")
                    
#             except Exception as e:
#                 errors += 1
#                 print(f"[DEBUG] Job {i}: ERROR saving - {str(e)}")
#                 continue
        
#         print(f"\n[DEBUG] === SAVE RESULTS ===")
#         print(f"[DEBUG] Created: {created}")
#         print(f"[DEBUG] Already existed: {updated}")
#         print(f"[DEBUG] Errors: {errors}")
#         print(f"[DEBUG] ===================\n")
        
#         return created

import os
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
import time

from django.conf import settings
from ..models import Job


def _parse_iso(dt: Optional[str]) -> Optional[datetime]:
    if not dt:
        return None
    try:
        if dt.endswith('Z'):
            return datetime.fromisoformat(dt.replace("Z", "+00:00"))
        return datetime.fromisoformat(dt)
    except Exception:
        return None


class JobFetcherService:
    """
    Enhanced job fetcher respecting user filters with robust error handling.
    """
    def __init__(self):
        self.jooble_key = getattr(settings, "JOOBLE_API_KEY", None)
        self.adzuna_app_id = getattr(settings, "ADZUNA_APP_ID", None)
        self.adzuna_app_key = getattr(settings, "ADZUNA_APP_KEY", None)
        self.rapidapi_key = getattr(settings, "RAPIDAPI_KEY", None)
        self.workable_token = getattr(settings, "WORKABLE_TOKEN", None)
        
        print(f"[DEBUG] API Keys Status:")
        print(f"  Jooble: {'✓' if self.jooble_key else '✗'}")
        print(f"  Adzuna: {'✓' if self.adzuna_app_id and self.adzuna_app_key else '✗'}")
        print(f"  RapidAPI: {'✓' if self.rapidapi_key else '✗'}")

    def fetch_from_jooble(self, keyword: str, location: str) -> List[Dict[str, Any]]:
        if not self.jooble_key:
            print("[DEBUG] Jooble: API key not set")
            return []
        
        url = f"https://jooble.org/api/{self.jooble_key}"
        payload = {"keywords": keyword, "location": location}
        print(f"[DEBUG] Jooble: Searching for '{keyword}' in '{location}'")

        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (compatible; JobBot/1.0)'
            }
            r = requests.post(url, json=payload, headers=headers, timeout=30)
            print(f"[DEBUG] Jooble: Status {r.status_code}")

            if r.status_code == 200:
                data = r.json()
                jobs_data = data.get("jobs", [])
                print(f"[DEBUG] Jooble: Found {len(jobs_data)} jobs")
                jobs = []
                for j in jobs_data:
                    jobs.append({
                        "title": (j.get("title") or "").strip(),
                        "company": (j.get("company") or "").strip(),
                        "location": (j.get("location") or "").strip(),
                        "salary_min": None,
                        "salary_max": None,
                        "link": j.get("link"),
                        "source": "jooble",
                        "posted_at": datetime.utcnow(),
                        "description": (j.get("snippet") or "")[:500]
                    })
                return [x for x in jobs if x.get("title") and x.get("link")]
            else:
                print(f"[DEBUG] Jooble: Error {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"[DEBUG] Jooble: Request failed - {str(e)}")
        
        return []

    def fetch_from_adzuna(self, keyword: str, location: str, country="ke") -> List[Dict[str, Any]]:
        if not (self.adzuna_app_id and self.adzuna_app_key):
            print("[DEBUG] Adzuna: Credentials not set")
            return []

        url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/1"
        params = {
            "app_id": self.adzuna_app_id,
            "app_key": self.adzuna_app_key,
            "what": keyword,
            "where": location,
            "results_per_page": 50,
            "content_type": "application/json",
            "sort_by": "date"
        }
        try:
            r = requests.get(url, params=params, timeout=30)
            print(f"[DEBUG] Adzuna: Status {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                jobs_data = data.get("results", [])
                jobs = []
                for j in jobs_data:
                    company = (j.get("company") or {}).get("display_name") or ""
                    loc = (j.get("location") or {}).get("display_name") or ""
                    jobs.append({
                        "title": (j.get("title") or "").strip(),
                        "company": company.strip(),
                        "location": loc.strip(),
                        "salary_min": j.get("salary_min"),
                        "salary_max": j.get("salary_max"),
                        "link": j.get("redirect_url"),
                        "source": f"adzuna_{country}",
                        "posted_at": _parse_iso(j.get("created")),
                        "description": (j.get("description") or "")[:500]
                    })
                return [x for x in jobs if x.get("title") and x.get("link")]
            else:
                print(f"[DEBUG] Adzuna: HTTP {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"[DEBUG] Adzuna: Request failed - {str(e)}")
        
        return []

    def fetch_from_rapidapi_jsearch(self, keyword: str, location: str) -> List[Dict[str, Any]]:
        if not self.rapidapi_key:
            print("[DEBUG] RapidAPI: Key not set")
            return []
        
        url = "https://jsearch.p.rapidapi.com/search"
        query = f"{keyword} in {location}" if location else keyword
        headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "jsearch.p.rapidapi.com"
        }
        params = {"query": query, "page": "1", "num_pages": "1", "date_posted": "all"}
        try:
            r = requests.get(url, headers=headers, params=params, timeout=30)
            print(f"[DEBUG] RapidAPI: Status {r.status_code}")
            if r.status_code == 200:
                data = r.json()
                jobs_data = data.get("data", [])
                jobs = []
                for j in jobs_data:
                    jobs.append({
                        "title": (j.get("job_title") or "").strip(),
                        "company": (j.get("employer_name") or "").strip(),
                        "location": (j.get("job_city") or "").strip() + ", " + (j.get("job_country") or "").strip(),
                        "salary_min": None,
                        "salary_max": None,
                        "link": j.get("job_apply_link"),
                        "source": "jsearch_rapidapi",
                        "posted_at": _parse_iso(j.get("job_posted_at_datetime_utc")),
                        "description": (j.get("job_description") or "")[:500]
                    })
                return [x for x in jobs if x.get("title") and x.get("link")]
        except Exception as e:
            print(f"[DEBUG] RapidAPI: Request failed - {str(e)}")
        
        return []

    def fetch_all(self, keyword: str, location: str, providers: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        providers = providers or ["jooble", "adzuna", "rapidapi"]
        results: List[Dict[str, Any]] = []
        print(f"[DEBUG] Job search: '{keyword}' in '{location}' with providers {providers}")

        for provider in providers:
            try:
                if provider == "jooble":
                    provider_results = self.fetch_from_jooble(keyword, location)
                elif provider == "adzuna":
                    provider_results = self.fetch_from_adzuna(keyword, location)
                elif provider == "rapidapi":
                    provider_results = self.fetch_from_rapidapi_jsearch(keyword, location)
                else:
                    print(f"[DEBUG] Unknown provider: {provider}")
                    continue
                results.extend(provider_results)
            except Exception as e:
                print(f"[DEBUG] {provider.upper()} fetch error: {str(e)}")
        
        # Deduplicate safely
        seen_links = set()
        seen_signatures = set()
        unique = []
        for job in results:
            title = (job.get("title") or "").lower().strip()
            company = (job.get("company") or "").lower().strip()
            signature = f"{title}::{company}"
            link = job.get("link")
            if link and signature not in seen_signatures and link not in seen_links:
                seen_links.add(link)
                seen_signatures.add(signature)
                unique.append(job)

        print(f"[DEBUG] Total unique jobs: {len(unique)}")
        return unique

    def save_jobs(self, jobs: List[Dict[str, Any]]) -> int:
        created = 0
        updated = 0
        errors = 0
        print(f"[DEBUG] Saving {len(jobs)} jobs")
        for i, job in enumerate(jobs, 1):
            if not job.get("link"):
                errors += 1
                continue
            try:
                defaults = {
                    "title": (job.get("title") or "")[:200],
                    "company": (job.get("company") or "")[:100],
                    "location": (job.get("location") or "")[:100],
                    "salary_min": job.get("salary_min"),
                    "salary_max": job.get("salary_max"),
                    "source": (job.get("source") or "")[:50],
                    "posted_at": job.get("posted_at") or datetime.utcnow(),
                    "description": (job.get("description") or "")[:1000] if hasattr(Job, 'description') else ""
                }
                obj, was_created = Job.objects.get_or_create(
                    link=job["link"][:500],
                    defaults=defaults
                )
                if was_created:
                    created += 1
                else:
                    updated += 1
            except Exception as e:
                errors += 1
        print(f"[DEBUG] Save results: Created={created}, Updated={updated}, Errors={errors}")
        return created


