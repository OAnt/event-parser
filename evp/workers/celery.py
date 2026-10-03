import os

from celery import Celery

redis = "redis://redis"
app = Celery(
    'tasks',
    backend=f"redis://{os.environ.get('EVP_CELERY_BACKEND')}",
    broker=f"redis://{os.environ.get('EVP_CELERY_BROKER')}",
)

if __name__ == "__main__":
    app.start()
