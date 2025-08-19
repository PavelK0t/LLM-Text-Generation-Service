from rest_framework import serializers
from .models import Job


class GenerateRequest(serializers.Serializer):
    prompt = serializers.CharField()
    provider = serializers.ChoiceField(choices=["openai", "huggingface"], required=False, default="openai")
    temperature = serializers.FloatField(required=False, default=0.7, min_value=0.0, max_value=2.0)
    max_tokens = serializers.IntegerField(required=False, default=256, min_value=16, max_value=4096)


class GenerateResponse(serializers.Serializer):
    text = serializers.CharField()
    provider = serializers.CharField()


class JobCreateRequest(GenerateRequest):
    pass


class JobSerializer(serializers.ModelSerializer):
    class Meta:
        model = Job
        fields = [
            "id",
            "prompt",
            "provider",
            "temperature",
            "max_tokens",
            "status",
            "result",
            "error",
            "created_at",
            "updated_at"
        ]
        read_only_fields = [
            "status",
            "result",
            "error",
            "created_at",
            "updated_at"
        ]


class JobCreateSerializer:
    class Meta:
        model = Job
        fields = "__all__"
