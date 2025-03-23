"""
This file contains Django REST Framework serializers used to convert model instances
to and from JSON representations.
"""

from rest_framework import serializers

from .models import UsageLog


class UsageLogSerializer(serializers.ModelSerializer):
    """
    A serializer class for the UsageLog model, enabling easy conversion
    between database records and JSON data.

    Fields:
        All fields from UsageLog for basic usage logging data.

    Example usage:
        serializer = UsageLogSerializer(instance=usage_log_obj)
        data = serializer.data  # returns a dict
    """

    class Meta:
        model = UsageLog
        fields = "__all__"


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for chat API requests.

    Attributes:
        thread_id (CharField): The unique identifier for the conversation thread.
        model (CharField): The AI model to use for the request.
        temperature (FloatField): The temperature setting for the AI model.
        message (CharField): The message content to send to the AI model.
    """

    thread_id = serializers.CharField(required=True)
    model = serializers.CharField(default="gpt-4o")
    temperature = serializers.FloatField(default=0.3)
    message = serializers.CharField(required=True)
