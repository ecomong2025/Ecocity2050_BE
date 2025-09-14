from django.db import models
from django.conf import settings

class SavedGameData(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_game'
    )
    co2_tons = models.FloatField(default=0)
    citizen_satisfaction = models.CharField(max_length=100, blank=True)
    budget = models.IntegerField(default=0)
    top_tags = models.TextField(blank=True)  # JSON 문자열로 저장
    ai_city_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'saved_game_data'
        verbose_name = '저장된 게임 데이터'
        verbose_name_plural = '저장된 게임 데이터들'

    def __str__(self):
        return f"{self.user}의 게임 데이터 ({self.updated_at})"
