"""Celery задачи для генерации текста."""
from __future__ import annotations
from celery import shared_task
from django.utils import timezone
from .models import Job
from .providers import generate_text
import asyncio


@shared_task(name="generator.run_generation")
def run_generation(job_id: str) -> None:
    """
    Фоновая задача генерации текста.
    - Забирает объект Job из БД.
    - Вызывает выбранного провайдера (OpenAI/HF).
    - Сохраняет результат и статус.
    """
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return

    job.status = "running"
    job.save(update_fields=["status"])

    try:
        result = asyncio.run(
            generate_text(
                prompt=job.prompt,
                provider=job.provider,
                temperature=job.temperature,
                max_tokens=job.max_tokens,
            )
        )
        job.result = result
        job.status = "done"
    except Exception as e:
        job.result = f"[ERROR] {e}"
        job.status = "failed"
    finally:
        job.updated_at = timezone.now()
        job.save(update_fields=["result", "status", "updated_at"])
