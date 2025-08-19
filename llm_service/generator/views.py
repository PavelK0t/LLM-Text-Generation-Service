"""Views для генерации текста через API."""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Job
from .serializers import JobSerializer, JobCreateSerializer
from .tasks import run_generation


@extend_schema(
    tags=["Text Generation"],
    summary="Управление задачами генерации текста",
    description=(
        "Эндпоинт для постановки задач на генерацию текста через OpenAI/HuggingFace.\n\n"
        "Поддерживает:\n"
        "- **POST /api/jobs/** → создать задачу (prompt, provider, параметры).\n"
        "- **GET /api/jobs/** → список задач.\n"
        "- **GET /api/jobs/{id}/** → получить статус и результат.\n"
        "- **POST /api/jobs/{id}/retry/** → повторно запустить задачу."
    )
)
class JobViewSet(viewsets.ModelViewSet):
    """
    ViewSet для управления задачами генерации текста.
    """

    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer

    def get_serializer_class(self):
        # Для создания используем отдельный сериализатор с валидацией входа
        if self.action == "create":
            return JobCreateSerializer
        return JobSerializer

    @extend_schema(
        summary="Создать задачу генерации текста",
        request=JobCreateSerializer,
        responses={
            201: OpenApiResponse(response=JobSerializer, description="Задача создана и отправлена в очередь"),
            400: OpenApiResponse(description="Ошибка валидации входных данных"),
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Создание новой задачи генерации текста.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job: Job = serializer.save()

        # Отправляем задачу в Celery
        run_generation.delay(str(job.id))

        return Response(JobSerializer(job).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Повторно запустить задачу",
        description="Если задача завершилась с ошибкой, можно перезапустить её.",
        responses={
            200: OpenApiResponse(response=JobSerializer, description="Задача перезапущена"),
            404: OpenApiResponse(description="Задача не найдена"),
        },
    )
    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        """
        Ручка для перезапуска задачи.
        """
        try:
            job = self.get_queryset().get(pk=pk)
        except Job.DoesNotExist:
            return Response({"detail": "Job not found"}, status=status.HTTP_404_NOT_FOUND)

        job.status = "pending"
        job.result = None
        job.save(update_fields=["status", "result"])

        run_generation.delay(str(job.id))

        return Response(JobSerializer(job).data, status=status.HTTP_200_OK)
