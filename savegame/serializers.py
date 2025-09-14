from rest_framework import serializers
from .models import SavedGameData

class SavedGameDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavedGameData
        fields = [
            "user",
            "co2_tons",
            "citizen_satisfaction",
            "budget",
            "top_tags",
            "ai_city_name",
            "created_at",
            "updated_at",
        ]
