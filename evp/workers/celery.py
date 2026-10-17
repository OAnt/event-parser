import os

from celery import Celery
from celery.signals import worker_ready

from evp.core.models.db import ensure_indexes

redis = "redis://redis"
app = Celery(
    'tasks',
    backend=f"redis://{os.environ.get('EVP_CELERY_BACKEND')}",
    broker=f"redis://{os.environ.get('EVP_CELERY_BROKER')}",
    include=["evp.workers.pipelines"],
)
app.conf.task_default_queue = "generic"


primary = os.environ.get('EVP_CELERY_PRIMARY', False)


@worker_ready.connect
def create_indexes(**kwargs):
    if primary:
        ensure_indexes()


if __name__ == "__main__":
    app.start()
