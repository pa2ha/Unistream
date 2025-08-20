
from celery import Celery
from config import settings

celery_app = Celery('Fastapi_proj',
                    broker=settings.CELERY_BROKER_URL,
                    backend=settings.CELERY_RESULT_BACKEND)
                    # include=['Users.tasks'])



@celery_app.task(name="pagman")
def create_task(task_type):
    return True