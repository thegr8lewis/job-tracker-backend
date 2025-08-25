from django.core.management.base import BaseCommand
from applications.tasks import fetch_jobs_daily

class Command(BaseCommand):
    help = "Fetch jobs from external APIs for all saved JobFilters (runs the same logic as the Celery task)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("Starting manual job fetch..."))
        result = fetch_jobs_daily()
        
        if result["jobs"] > 0 or result["applications"] > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Done. Fetched {result['jobs']} new jobs and created {result['applications']} new applications."
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("No new jobs or applications were created. Check debug output for details.")
            )