from celery import shared_task

from .utils.sync_google_candidate import Candidate_GoogleSheet_Data

@shared_task(bind=True, max_retries=3)
def sync_candidates(self, sheet_id):
    """
    Task to sync candidates for a specific Job.
    """
    try:
        result = Candidate_GoogleSheet_Data(sheet_id)
        return result
    except Exception as e:
        raise self.retry(exc=e, countdown=60)  # retry after 1 minute
