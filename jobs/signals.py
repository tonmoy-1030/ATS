from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from .models import Job
import json

@receiver(post_save, sender=Job)
def create_or_update_job_task(sender, instance, created, **kwargs):
    """
    Automatically create/update a Celery Beat task for this Job.
    Enable task if job is open, disable if closed.
    """
    task_name = f"sync_{instance.google_sheet_id}_{instance.job_title}"
    
    schedule, _ = CrontabSchedule.objects.get_or_create(
        minute="*/5",
        hour="*",
        day_of_week="*",
        day_of_month="*",
        month_of_year="*",
    )
    
    if instance.open_status and instance.google_sheet_id:
        PeriodicTask.objects.update_or_create(
            name = task_name,
            defaults={
                'crontab': schedule,
                "task": "candidates.tasks.sync_candidates",
                "args": json.dumps([instance.google_sheet_id]),
                "enabled": True
            }
        )
        
    else:
        try:
            task = PeriodicTask.objects.get(name=task_name)
            task.enabled=False
            task.save()
        except PeriodicTask.DoesNotExist:
            pass
    
    @receiver(post_delete, sender=Job)
    def delete_job_task(sender, instance, **kwargs):
        """Delete the periodic task if the Job is deleted"""
        task_name = f"sync_job_{instance.google_sheet_id}"
        PeriodicTask.objects.filter(name=task_name).delete()