import uuid
from django.db import models


class Job(models.Model):
    """Модель фоновой задачи генерации текста."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        RUNNING = "RUNNING", "Running"
        DONE = "DONE", "Done"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    prompt = models.TextField()
    provider = models.CharField(max_length=32, default="openai")
    temperature = models.FloatField(default=0.7)
    max_tokens = models.IntegerField(default=256)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    result = models.TextField(blank=True)
    error = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Job({self.id}) {self.status}"
