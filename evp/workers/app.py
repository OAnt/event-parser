from celery import Celery

redis = "redis://redis"
app = Celery('tasks', backend=redis, broker=redis)
