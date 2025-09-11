from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.utils import timezone


class CustomUser(AbstractUser):
    pass


class KakaoAuthSession(models.Model):
    """Unity 카카오 로그인을 위한 세션 관리"""
    state = models.CharField(max_length=255, unique=True, default=uuid.uuid4)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)

    # 세션 만료
    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timezone.timedelta(minutes=10)

    def __str__(self):
        return f"KakaoSession({self.state[:8]}... - {self.is_completed})"

    class Meta:
        ordering = ['-created_at']