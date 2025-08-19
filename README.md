# LLM-Text-Generation-Service
Продакшен‑образец сервиса генерации текстов через LLM с двумя провайдерами (OpenAI / Hugging Face), синхронным REST‑методом и асинхронной постановкой задач в очередь (Celery + Redis), удобной HTML-формой, логированием, тестами и Docker‑окружением.

## Запуск
1. Скопируйте `.env.example` в `.env` и задайте ключи API.
2. Запустите через Docker:
```bash
docker compose up --build
```
