"""Унифицированный слой работы с провайдерами LLM."""
from __future__ import annotations
import os
import httpx
from typing import Literal
from django.conf import settings


Provider = Literal["openai", "huggingface"]


async def generate_text(prompt: str, provider: Provider = None, temperature: float = 0.7, max_tokens: int = 256) -> str:
    provider = provider or settings.PROVIDER


    if provider == "openai":
        return await _openai(prompt, temperature, max_tokens)
    elif provider == "huggingface":
        return await _huggingface(prompt, temperature, max_tokens)
    else:
        raise ValueError(f"Unsupported provider: {provider}")


async def _openai(prompt: str, temperature: float, max_tokens: int) -> str:
    """Вызов OpenAI Chat Completions API (модель gpt-4o-mini как пример)."""
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        # Позволяет запускать проект без ключа (для демо) — возвращаем эхо‑ответ
        return f"[DEMO] OpenAI echo: {prompt[:200]}"

    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def _huggingface(prompt: str, temperature: float, max_tokens: int) -> str:
    """HF Inference API (пример: meta-llama/Meta-Llama-3-8B-Instruct)."""
    token = settings.HF_API_TOKEN
    if not token:
        return f"[DEMO] HF echo: {prompt[:200]}"

    url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3-8B-Instruct"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "inputs": prompt,
        "parameters": {"max_new_tokens": int(max_tokens), "temperature": float(temperature)},
    }
    async with httpx.AsyncClient(timeout=120) as client:
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"].strip()
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"].strip()
        return str(data)[:1000]
